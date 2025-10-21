from fastapi import FastAPI, Body, Form, File, UploadFile 
from enum import Enum
from pydantic import BaseModel

app = FastAPI()

@app.post("/files")
async def upload_multiple_files(files: list[UploadFile] = File(...)):
    return [
        {"file_name": file.filename,
         "content_type": file.content_type} for file in files
    ]

# @app.get("/")
# async def hello_world():
#     """
#     1. We define GET endpoint at the root path.
#     2. It produces a proper HTTP response with a JSON payload.
#     3. A decorator is a syntatic sugar that allows you to wrap a function or class with common logic without compromising readability.
#     4. FastAPI exposes one decorator per HTTP method to add new routes to the application.
#     5. FastAPI exposes an Asynchronous Server Gateway Interface (ASGI) - compatible application.
#     """
#     return {"hello": "world"}

