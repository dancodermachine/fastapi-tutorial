from pathlib import Path

import torch
from PIL import Image, ImageDraw, ImageFont
from transformers import YolosForObjectDetection, YolosImageProcessor

# 1. Load an image from the disk using Pillow.
# 2. Load a pretrained object detection model.
# 3. Run the model on our image.
# 4. Display the results by drawing rectangles around the detected objects.

root_directory = Path(__file__).parent.parent
picture_path = root_directory / "images" / "coffee-shop.jpg"

image = Image.open(picture_path)

image_processor = YolosImageProcessor.from_pretrained("hustvl/yolos-tiny")
# YOLOS is a cutting-edge approach to object detection that has been trained on 118k annotated images.
model = YolosForObjectDetection.from_pretrained("hustvl/yolos-tiny")

inputs = image_processor(images=image, return_tensors="pt")
outputs = model(**inputs)

target_sizes = torch.tensor([image.size[::-1]])
results = image_processor.post_process_object_detection(
    outputs, target_sizes=target_sizes
)[0]

draw = ImageDraw.Draw(image)
# font_path = root_directory / "assets" / "OpenSans-ExtraBold.ttf"
# font = ImageFont.truetype(str(font_path), 24)
for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
    # labels: The list of labels of each detected object.
    # boxes: The coordinates of the bounding box of each detected object.
    # scores: The confidence score of the algorithm for each detected object.
    if score > 0.7:
        box_values = box.tolist()
        label = model.config.id2label[label.item()]
        draw.rectangle(box_values, outline="red", width=5)
        draw.text(box_values[0:2], label, fill="red") # font=font
image.show()