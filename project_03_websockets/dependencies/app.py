from fastapi import Cookie, FastAPI, WebSocket, WebSocketException, status
from starlette.websockets import WebSocketDisconnect

API_TOKEN = "SECRET_API_TOKEN"

app = FastAPI()

"""
Basic dependencies such as Query, Header, or Cookie work transparently.

There is no way to pass custom headers. This means that if you rely on headers for authentication, you'll have to either add one using cookies or implement an authentication message mechanism in the WebSocket logic itself. However, if you don't plan to use your WebSocket with a browser, you can still rely on headers since most WebSocket clients support them.
"""

@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, username: str = "Anonymous", token: str = Cookie(...)
):
    if token != API_TOKEN:
        # Under the hood, FastAPI will handle this exception by closing the WebSocket with the specified status code. WebSockets have their own set of status code.  
        raise WebSocketException(status.WS_1008_POLICY_VIOLATION)

    await websocket.accept()

    await websocket.send_text(f"Hello, {username}!")
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        pass