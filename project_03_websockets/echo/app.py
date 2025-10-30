from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # `accept` method should be called first as it tells the cleint that we agree to open the tunnel
    await websocket.accept()
    try:
        # We start an infinite loop. We are opening a communication channel, it'll remain open until the client or the server decides to close it.
        while True:
            # `receive_text` returns the data sent by the client in plain text format. It's important here to understand that this method will block until data is received from the client.
            data = await websocket.receive_text()
            # When data is received, the method returns the text data and we can proceed with the next line. Here, we simply send back the message to the client thanks to the `send_text` method.
            await websocket.send_text(f"Message text was: {data}")
            # Once done, we are going back to the beginning of the loop to wait for another message.
    except WebSocketDisconnect:
    # try ... except is necessary to handle client disconnection. Most of the time, our server will be blocked at the `receive_text` line, waiting for the client data. If the client decides to disconnect, the tunnel will be closed and the `receive_text` call will fail, with a `WebSocketDisconnect` exception. That's why it's important to catch it to break tthe loop and properly finish the function.
        pass