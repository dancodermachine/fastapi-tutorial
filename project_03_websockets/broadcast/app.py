import asyncio
import contextlib

from broadcaster import Broadcast
from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from starlette.websockets import WebSocketDisconnect

# Broadcast only expects a URL to our Redis server.
broadcast = Broadcast("redis://localhost:6379")
# Notice also that we define a CHANNEL constant. This will be the name of the channel to publish and subscribe to messages. We choose a static value here for the sake of the example, but you could have dynamic channel names in a real-world application - to support sever chat rooms
CHANNEL = "CHAT"


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """
    We tell FastAPI to open the connection with the broker when it starts the application and to close it when exiting.
    """
    await broadcast.connect()
    yield
    await broadcast.disconnect()


app = FastAPI(lifespan=lifespan)


class MessageEvent(BaseModel):
    username: str
    message: str


async def receive_message(websocket: WebSocket, username: str):
    """
    Subscribe to new messages and send them to the client. 
    """
    # Subscribe to the broadcast channel
    async with broadcast.subscribe(channel=CHANNEL) as subscriber:
        # Waits for messages called `event`.
        async for event in subscriber:
            # `event.message` contains serialized JSON that we deserialized to instantiate a `MessageEvent` object.
            # Notie we use the `parse_raw` method for the Pydantic model, allowing us to parse the JSON string into an object in one operation
            message_event = MessageEvent.parse_raw(event.message)
            # Discard user's own messages.
            # We check whether the message username is different from the current username. Indeed, since all users are subscribed to the channel, they will also receive the messages they sent themselves. That's why we discard them based on the username to avoid this. Of course, in a real-world application, you'll likely want to rely on a unique user ID rather than a simple username.
            if message_event.username != username:
                # We can send the message through the WebSocket thanks to the `send_json` method, which takes care of serialising the dictionary automatically.
                await websocket.send_json(message_event.dict())


async def send_message(websocket: WebSocket, username: str):
    """
    Publish messages received in the WebSocket to the broker.
    """
    # Waits for data in the socket
    data = await websocket.receive_text()
    # Structures it into a MessageEvent object
    event = MessageEvent(username=username, message=data)
    # Publishes it
    await broadcast.publish(channel=CHANNEL, message=event.json())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, username: str = "Anonymous"):
    await websocket.accept()
    try:
        while True:
            receive_message_task = asyncio.create_task(
                receive_message(websocket, username)
            )
            send_message_task = asyncio.create_task(send_message(websocket, username))
            done, pending = await asyncio.wait(
                {receive_message_task, send_message_task},
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
            for task in done:
                task.result()
    except WebSocketDisconnect:
        pass