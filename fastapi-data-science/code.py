from fastapi import (FastAPI,
                     Body,
                     Form,
                     File,
                     UploadFile,
                     Header,
                     Cookie,
                     Request,
                     status,
                     Response,
                     HTTPException)
from fastapi.responses import (HTMLResponse,
                               PlainTextResponse,
                               RedirectResponse,
                               FileResponse) 
from enum import Enum
from pydantic import BaseModel

app = FastAPI()


@app.get("/html", response_class=HTMLResponse)
async def get_html():
    return """
        <html>
            <head>
                <title>Hello world!</title>
            </head>
            <body>
                <h1>Hello world!</h1>
            </body>
        </html>
    """


@app.get("/text", response_class=PlainTextResponse)
async def text():
    return "Hello world!"

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

