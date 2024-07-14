from threading import Event
from translation.AudioPipeline import AudioPipeline
from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging

class AppState:
    def __init__(self):
        self.audio_pipeline = AudioPipeline(chunk_duration=10, overlap_duration=2)
        self.transcription_thread = None
        self.stop_event = Event()


@asynccontextmanager
async def lifespan(app: FastAPI):
    state = AppState()
    app.state.state = state
    logging.info("Starting API server...")
    yield
    logging.info("Shutting down API server...")
    state.stop_event.set()
    if state.transcription_thread is not None:
        state.transcription_thread.join()
    state.audio_pipeline.stop_audio_stream() 
    logging.info("Server has been shutdown gracefully.")