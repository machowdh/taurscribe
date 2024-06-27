from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from audio import AudioStreamer
import uvicorn

app = FastAPI()


@app.websocket("/wss/translate")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # while True:
    #     audio_streamer = AudioStreamer()
    #     try:
    #         async for audio_chunk in audio_streamer.stream_audio():
    #             translation = translate_audio(translate_audio)
    #             await websocket.send_text(translation)
    #     except WebSocketDisconnect:
    #         pass

def start_api_server():
    try:
        uvicorn.run(app, host='0.0.0.0', port=8008, log_level='info')    
        return True
    except:
        return False

if __name__ == '__main__':
    start_api_server()
