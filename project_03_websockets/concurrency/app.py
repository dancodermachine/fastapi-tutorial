import asyncio
from datetime import datetime

from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

app = FastAPI()

"""
In the echo folder example, we assumed that the client was always sending message first: we wait for its message before sending it back. Once again, it's the client that takes the initiative in the conversation. However, in usual scenarios, the server can have data to send to the client without being at the initiative. In a chat application, another user can typically send one or several messages that we want to forward to the first user immediately. In this context, the blocking call to `receive_text` we showed in the previous example is a problem: while we are waiting, the server could have messages to forward to the client.

`asyncio` provides functions that allow us to schedule several coroutines concurrently and wait until one of them is complete. We can have a coroutine that waits for client messages and another one that sends data to it when it arrives. The first one that is fulfilled wins and we can start again with another loop interation.
"""

async def echo_message(websocket: WebSocket):
    """
    Waits for text messages from the client and sends them back.
    """
    data = await websocket.receive_text()
    await websocket.send_text(f"Message text was: {data}")

async def send_time(websocket: WebSocket):
    """
    Waits for 10 seconds before sending the current time to the client.
    """
    await asyncio.sleep(10)
    await websocket.send_text(f"It is: {datetime.utcnow().isoformat()}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            """
            We call our 2 functions, wrapped by the `create_task` function of asyncio. This transforms the coroutine into a `task` object. Under the hood, a task is how the event loop manages the execution of the coroutine. Under the hood, a task is how the event loop manages the execution of the coroutine. Put more simply, it gives us full control over the execution of the coroutine - we can retrieve its result or even cancel it.
            """
            echo_message_task = asyncio.create_task(echo_message(websocket))
            send_time_task = asyncio.create_task(send_time(websocket))
            """
            `asyncio.wait` is a function especially useful for running tasks concurrently. By default, this function will block until all given tasks are completed. However, we can control that thanks to the `return_when` argument: in our case, we want it to block until one of the tasks is completed, which corresponds to the `FIRST_COMPLETED` value. The effect is the following: our server will launch the coroutines concurrently. The first one will block waiting for a client message, while the other one will block for 10 seconds. If the client sends a message before 10 seconds have passed, it'll send the message back and complete. Otherwise, the `send_time` coroutine will send the current time and complete.
            At this point, `asyncio.wait` will return us two sets: the first one, `done`, contains a set of completed tasks, while the other one, `pending`, contains a set of tasks not yet completed. 
            """
            done, pending = await asyncio.wait(
                {echo_message_task, send_time_task},
                return_when=asyncio.FIRST_COMPLETED,
            )
            """
            Before starting the loop again, we need to first cancel all the tasks that have not been completed.
            """
            for task in pending:
                task.cancel()
            for task in done:
                # `.result()` returns the result of the coroutine but also re-raises an execption that could have been raised inside.
                task.result()
    except WebSocketDisconnect:
        pass