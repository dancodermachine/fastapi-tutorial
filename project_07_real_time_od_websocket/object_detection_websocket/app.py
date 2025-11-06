import asyncio
import contextlib
import io
from pathlib import Path

import torch
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from pydantic import BaseModel
from transformers import YolosForObjectDetection, YolosImageProcessor

"""
Implement a WebSocket endpoint that is able to both accept data and run object detection on it. The main challenge here will be to handle a phenomenon known as backpressure. Put simply, we'll receive more images from the browser than the server is able to handle because of the time needed to run the detection algorithm. Thus, we'll have to work with a queue (or buffer) of limited size and drop some images along the way to handle the stream in near real time.
"""

class Object(BaseModel):
    box: tuple[float, float, float, float]
    label: str


class Objects(BaseModel):
    objects: list[Object]


class ObjectDetection:
    image_processor: YolosImageProcessor | None = None
    model: YolosForObjectDetection | None = None

    def load_model(self) -> None:
        """Loads the model"""
        self.image_processor = YolosImageProcessor.from_pretrained("hustvl/yolos-tiny")
        self.model = YolosForObjectDetection.from_pretrained("hustvl/yolos-tiny")

    def predict(self, image: Image.Image) -> Objects:
        """Runs a prediction"""
        if not self.image_processor or not self.model:
            raise RuntimeError("Model is not loaded")
        inputs = self.image_processor(images=image, return_tensors="pt")
        outputs = self.model(**inputs)

        target_sizes = torch.tensor([image.size[::-1]])
        results = self.image_processor.post_process_object_detection(
            outputs, target_sizes=target_sizes
        )[0]

        objects: list[Object] = []
        for score, label, box in zip(
            results["scores"], results["labels"], results["boxes"]
        ):
            if score > 0.7:
                box_values = box.tolist()
                label = self.model.config.id2label[label.item()]
                objects.append(Object(box=box_values, label=label))
        return Objects(objects=objects)


object_detection = ObjectDetection()


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    object_detection.load_model()
    yield


app = FastAPI(lifespan=lifespan)

# asyncio.Queue is a convenient structure allowing us to queue some data in memory and retrieve it in a first in, first out (FIFO) strategy. We are able to set a limit on the number of elements we store in the queue: this is how we'll be able to limit the number of images we handle.

async def receive(websocket: WebSocket, queue: asyncio.Queue):
    """
    Waits for raw bytes from the WebSocket. 
    The receive function receives data and puts it at the end of the queue. When working with asyncio.Queue, we have two methods to put a new element in the queue: put and put_nowait. If the queue is full, the first one will wait until there is room in the queue. This is not what we want here: we want to drop images that we won't be to handle in time. With put_nowait, the QueueFull exception is raised if the queue is full. In this case, we just pass and drop the data.
    """
    while True:
        bytes = await websocket.receive_bytes()
        try:
            queue.put_nowait(bytes)
        except asyncio.QueueFull:
            pass


async def detect(websocket: WebSocket, queue: asyncio.Queue):
    """
    Performing the detection and sending the result. The detect function pulls the first message from the queue and runs its detection before sending the result. Notice that since we get raw image bytes directly, we have to wrap them with io.BytesIO to make it acceptable for Pillow.
    """
    while True:
        bytes = await queue.get()
        image = Image.open(io.BytesIO(bytes))
        objects = object_detection.predict(image)
        await websocket.send_json(objects.dict())


@app.websocket("/object-detection")
async def ws_object_detection(websocket: WebSocket):
    """
    We are scheduling both tasks and waiting until one of them has stopped. Since they both run an infinite loop, this will happen when the WebSocket is disconnected.
    """
    await websocket.accept()
    queue: asyncio.Queue = asyncio.Queue(maxsize=1)
    receive_task = asyncio.create_task(receive(websocket, queue))
    detect_task = asyncio.create_task(detect(websocket, queue))
    try:
        done, pending = await asyncio.wait(
            {receive_task, detect_task},
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()
        for task in done:
            task.result()
    except WebSocketDisconnect:
        pass


@app.get("/")
async def index():
    return FileResponse(Path(__file__).parent / "index.html")


static_files_app = StaticFiles(directory=Path(__file__).parent / "assets")
app.mount("/assets", static_files_app)