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
from enum import Enum
from pydantic import BaseModel

app = FastAPI()


@app.post("/password")
async def check_password(password: str = Body(...), password_confirm: str = Body(...)):
    if password != password_confirm:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Passwords don't match.",
                "hints": [
                    "Check the caps lock on your keyboard",
                    "Try to make the password visible by clicking on the eye icon to check your typing",
                ],
            },
        )
    return {"message": "Passwords match."}

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

