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

@app.get("/")
async def get():
    return HTMLResponse("""
        <html>
            <head>
                <title>WebSocket</title>
            </head>
            <body>
                <h1>WebSocket Audio Streaming</h1>
                <br><br>
                <button onclick="startRecording()">Start Recording</button>
                <button onclick="stopRecording()">Stop Recording</button>
                <div id="transcription" style="white-space: pre-wrap; margin-top: 20px; border: 1px solid black; padding: 10px;"></div>
                <script>
                    var ws;
                    function startRecording() {
                        ws = new WebSocket("ws://localhost:8008/ws");
                        ws.onopen = function() {
                            console.log("WebSocket is open now.");
                            const message = JSON.stringify({command: 'start'});
                            ws.send(message);
                        };
                        ws.onmessage = function(event) {
                            console.log("Received from server: " + event.data);
                            document.getElementById("transcription").innerText += event.data + "\\n";
                        };
                        ws.onerror = function(event) {
                            console.error("WebSocket error observed:", event);
                        };
                        ws.onclose = function() {
                            console.log("WebSocket is closed now.");
                        };
                    }
                    function stopRecording() {
                        if (ws) {
                            const message = JSON.stringify({command: 'stop'});
                            ws.send(message);
                            ws.close();
                        }
                    }
                </script>
            </body>
        </html>
    """)

def start_api_server():
    try:
        uvicorn.run(app, host='0.0.0.0', port=8008, log_level='info')
    except Exception as e:
        logging.error(f"Error starting API server: {e}")

if __name__ == "__main__":
    start_api_server()
