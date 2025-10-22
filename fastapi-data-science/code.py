from fastapi import FastAPI, Body, Form, File, UploadFile, Header, Cookie, Request, status 
from enum import Enum
from pydantic import BaseModel

app = FastAPI()


class Post(BaseModel):
        title: str
        nb_views: int

class PublicPost(BaseModel):
    title: str

# Dummy database
posts = {
    1: Post(title="Hello", nb_views=100),
}

@app.get("/posts/{id}", response_model=PublicPost)
async def get_post(id: int):
    return posts[id]

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

