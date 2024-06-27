from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
# from audio import AudioStreamer
import uvicorn

import logging

# Set up logging
logging.basicConfig(filename='sidecar.log', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s %(message)s')

app = FastAPI()

PORT_API = 8008

origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logging.info("WebSocket connection established")
    await websocket.send_text('Reached')
    
    # try:
    #     while True:
    #         data = await websocket.receive_text()
    #         print(f"Received message: {data}")
    #         await websocket.send_text(f"Message: {data}")
    # except WebSocketDisconnect:
        # print("WebSocket connection closed")

def start_api_server():
    try:
        print("Starting API server...")
        uvicorn.run(app, host='0.0.0.0', port=8008, log_level='info')    
        return True
    except Exception as e:
        logging.error(f"Error starting API server: {e}")
        return False

if __name__ == '__main__':
    start_api_server()
