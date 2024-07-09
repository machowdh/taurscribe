from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from audio.AudioStreamer import AudioStreamer
from translation.AudioPipeline import AudioPipeline
from queue import Queue
from threading import Thread
import uvicorn
import logging
import asyncio
import json
import numpy as np
import wave

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

app = FastAPI()

PORT_API = 8008

origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

audio_pipeline = AudioPipeline()
audio_streamer = AudioStreamer()

BUFFER_SIZE = 16000  # Process in 1-second chunks

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    loop = asyncio.get_event_loop()
    audio_thread = None
    try:
        while True:
            data = await websocket.receive_text()
            logging.info(f"Received data: {data}")
            try:
                command_data = json.loads(data)
                command = command_data.get("command")
                language = command_data.get("language", "en")
            except json.JSONDecodeError:
                logging.error("Invalid JSON received")
                continue

            if command == 'start':
                logging.info("Starting audio stream")
                audio_streamer.start_audio_stream()
                if audio_thread is None:
                    audio_thread = loop.run_in_executor(None, process_audio, websocket, language)
            elif command == 'stop':
                logging.info("Stopping audio stream")
                audio_streamer.stop_audio_stream()
                if audio_thread:
                    audio_thread = None
    except WebSocketDisconnect:
        logging.info("WebSocket disconnected")
        audio_streamer.stop_audio_stream()
        if audio_thread:
            audio_thread = None
    except Exception as e:
        logging.error(f"WebSocket error: {e}")


def process_audio(websocket, language):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(process_audio_async(websocket, language))


async def process_audio_async(websocket, language):
    while audio_streamer._running:
        await asyncio.sleep(1)  # Wait for some data to be collected

    logging.info("Processing audio data from temp.wav")
    transcription = audio_pipeline.translate('temp.wav', language)
    logging.info(f"Transcription: {transcription}")
    try:
        await websocket.send_text(transcription)
        logging.info(f"Sent transcription: {transcription}")
    except Exception as e:
        logging.error(f"Error sending transcription: {e}")

@app.get("/")
async def get():
    return HTMLResponse("""
        <html>
            <head>
                <title>WebSocket</title>
            </head>
            <body>
                <h1>WebSocket Audio Streaming</h1>
                <label for="language">Select Language:</label>
                <select id="language">
                    <option value="english">English</option>
                    <option value="japanese">Japanese</option>
                    <option value="es">Spanish</option>
                    <option value="fr">French</option>
                    <!-- Add more languages as needed -->
                </select>
                <br><br>
                <button onclick="startRecording()">Start Recording</button>
                <button onclick="stopRecording()">Stop Recording</button>
                <div id="transcription" style="white-space: pre-wrap; margin-top: 20px; border: 1px solid black; padding: 10px;"></div>
                <script>
                    var ws;
                    function startRecording() {
                        var language = document.getElementById("language").value;
                        ws = new WebSocket("ws://localhost:8008/ws");
                        ws.onopen = function() {
                            console.log("WebSocket is open now.");
                            const message = JSON.stringify({command: 'start', language: language});
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
        logging.info("Starting API server...")
        uvicorn.run(app, host='0.0.0.0', port=PORT_API, log_level='info')
        return True
    except Exception as e:
        logging.error(f"Error starting API server: {e}")
        return False


if __name__ == "__main__":
    start_api_server()
