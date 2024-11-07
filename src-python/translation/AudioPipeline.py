import logging
from transformers import pipeline
from queue import Queue
import numpy as np
import pyaudiowpatch as pyaudio
import torchaudio
import torch
import time
import asyncio

class AudioPipeline:
    def __init__(self, chunk_duration=10, overlap_duration=2):
        self.pipe = None  # Delay initialization
        self.p = pyaudio.PyAudio()
        self.WHISPER_SAMPLE_RATE = 16000

        self.stream = None
        self.format = pyaudio.paFloat32
        self.channels = 1
        self._running = False
        self.audio_queue = Queue()

        self.chunk_duration = chunk_duration
        self.overlap_duration = overlap_duration

        self.buffer = np.array([], dtype=np.float32)
        try:
            self.wasapi_info = self.p.get_host_api_info_by_type(pyaudio.paWASAPI)
        except OSError:
            exit()
        
        self.default_speakers = self.p.get_device_info_by_index(self.wasapi_info['defaultOutputDevice'])

        if not self.default_speakers['isLoopbackDevice']:
            for loopback in self.p.get_loopback_device_info_generator():
                if self.default_speakers['name'] in loopback['name']:
                    self.default_speakers = loopback
                    break
            else:
                exit()
        
        self.rate = int(self.default_speakers['defaultSampleRate'])
        self.frames_per_buffer = int(self.rate * 0.1)

    def initialize_pipe(self):
        if self.pipe is None:  # Initialize only once
            self.pipe = pipeline("automatic-speech-recognition", model="openai/whisper-tiny")

    def callback(self, in_data, frame_count, time_info, status):
        audio_data = np.frombuffer(in_data, dtype=np.float32)
        self.audio_queue.put(audio_data)
        return (in_data, pyaudio.paContinue)
    
    def resample(self, waveform, src_sample_rate, target_sample_rate):
        waveform = torch.from_numpy(waveform).float()
        resampler = torchaudio.transforms.Resample(src_sample_rate, target_sample_rate)
        resampled_waveform = resampler(waveform)
        return resampled_waveform.numpy()

    def transcribe_audio(self, websocket, stop_event):
        self.initialize_pipe()  # Ensure pipe is initialized for transcription
        while not stop_event.is_set():
            if self._running:
                if not self.audio_queue.empty():
                    self.buffer = np.concatenate((self.buffer, self.audio_queue.get()))

                    if len(self.buffer) >= self.rate * self.chunk_duration:
                        resampled_audio = self.resample(self.buffer, self.rate, self.WHISPER_SAMPLE_RATE)
                        transcription = self.pipe({'array': resampled_audio, 'sampling_rate': self.WHISPER_SAMPLE_RATE}, generate_kwargs={"task": "translate", "language": "en"})
                        asyncio.run(self.send_transcription(websocket, transcription["text"]))
                        self.buffer = self.buffer[len(self.buffer) - int(self.rate * self.overlap_duration):]
                else:
                    time.sleep(0.1)
            else:
                time.sleep(0.1)

    async def send_transcription(self, websocket, transcription):
        try:
            await websocket.send_text(transcription)
        except Exception as e:
            logging.error(f'Error sending transcription {e}')

    def start_audio_stream(self):
        self.initialize_pipe()  # Lazy initialization
        self.stream = self.p.open(format=self.format,
                                  channels=self.channels,
                                  rate=self.rate,
                                  input=True,
                                  frames_per_buffer=self.frames_per_buffer,
                                  stream_callback=self.callback,
                                  input_device_index=self.default_speakers['index'])
        self.stream.start_stream()
        self._running = True

    def stop_audio_stream(self):
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self._running = False
        self.audio_queue.queue.clear()