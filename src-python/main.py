from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app_state import lifespan
from threading import Thread
import asyncio
import uvicorn
import logging
import json

logging.basicConfig(level=logging.INFO,
                    filename='sidecar.log',
                    format='%(asctime)s %(levelname)s %(message)s')

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
                logging.info("Starting Audio Stream")
                if state.transcription_thread is None or not state.transcription_thread.is_alive():
                    state.transcription_thread = Thread(target=state.audio_pipeline.transcribe_audio, args=(websocket, state.stop_event))
                    state.transcription_thread.start()
            elif command == 'stop':
                state.audio_pipeline.stop_audio_stream()
    except WebSocketDisconnect:
        state.audio_pipeline.stop_audio_stream()
        state.stop_event.set()
        if state.transcription_thread is not None:
            state.transcription_thread.join()
        logging.info("WebSocket disconnected, transcription stopped.")


@app.get("/")
async def get():
    return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>WebSocket Test</title>
            <style>
                body { font-family: Arial, sans-serif; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .messages { border: 1px solid #ccc; padding: 10px; height: 300px; overflow-y: scroll; }
                .button { padding: 10px 15px; margin: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>WebSocket Test</h1>
                <div>
                    <button id="startButton" class="button">Start Recording</button>
                    <button id="stopButton" class="button">Stop Recording</button>
                </div>
                <div class="messages" id="messages"></div>
            </div>
            <script>
                let websocket;
                const messagesDiv = document.getElementById('messages');

                document.getElementById('startButton').addEventListener('click', () => {
                    if (!websocket || websocket.readyState === WebSocket.CLOSED) {
                        websocket = new WebSocket("ws://localhost:8008/ws");
                        
                        websocket.onopen = () => {
                            messagesDiv.innerHTML += '<p>WebSocket is open now.</p>';
                            websocket.send(JSON.stringify({ command: "start" }));
                        };
                        
                        websocket.onmessage = (event) => {
                            messagesDiv.innerHTML += '<p>Received: ' + event.data + '</p>';
                            messagesDiv.scrollTop = messagesDiv.scrollHeight;
                        };
                        
                        websocket.onerror = (event) => {
                            messagesDiv.innerHTML += '<p style="color: red;">WebSocket error: ' + event + '</p>';
                        };
                        
                        websocket.onclose = () => {
                            messagesDiv.innerHTML += '<p>WebSocket is closed now.</p>';
                        };
                    } else if (websocket.readyState === WebSocket.OPEN) {
                        websocket.send(JSON.stringify({ command: "start" }));
                    }
                });

                document.getElementById('stopButton').addEventListener('click', () => {
                    if (websocket && websocket.readyState === WebSocket.OPEN) {
                        websocket.send(JSON.stringify({ command: "stop" }));
                    }
                });
            </script>
        </body>
        </html>
    """)


async def run_server():
    config = uvicorn.Config(app, host='0.0.0.0', port=8008, log_level='info')
    server = uvicorn.Server(config)
    await server.serve()

def start_api_server():
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(run_server())
    except KeyboardInterrupt:
        logging.info("Shutting down the server gracefully.")
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

if __name__ == "__main__":
    start_api_server()