from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app_state import lifespan
from threading import Thread
import uvicorn
import logging
import json

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    state = app.state.state
    try:
        while True:
            data = await websocket.receive_text()
            command_data = json.loads(data)
            command = command_data.get("command")
            if command == 'start':
                state.audio_pipeline.start_audio_stream()
                if state.transcription_thread is None or not state.transcription_thread.is_alive():
                    state.transcription_thread = Thread(target=state.audio_pipeline.transcribe_audio, args=(websocket, state.stop_event))
                    state.transcription_thread.start()
            elif command == 'stop':
                state.audio_pipeline.stop_audio_stream()
    except WebSocketDisconnect:
        state.audio_pipeline.stop_audio_stream()

def start_api_server():
    try:
        uvicorn.run(app, host='0.0.0.0', port=8008, log_level='info')
    except Exception as e:
        logging.error(f"Error starting API server: {e}")

if __name__ == "__main__":
    start_api_server()
