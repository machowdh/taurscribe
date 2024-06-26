from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from audio import audiostreamer


app = FastAPI()


@app.websocket("/ws/translate")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        # data = await websocket.receive_bytes()
        