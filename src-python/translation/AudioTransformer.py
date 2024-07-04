from transformers import WhisperProcessor, WhisperForConditionalGeneration
from audio import AudioStreamer
import pyaudiowpatch as pyaudio
import wave
import time

class AudioTransformer:
    def __init__(self):
        self.model_name = "openai/whisper-tiny"
        self.processor = WhisperProcessor.from_pretrained("openai/whisper-tiny")
        self.model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-tiny")
    
    def translate(self, origin_language, streamer):
        input_features = self.processor(streamer.audio_chunk, sampling_rate=streamer.rate, return_tensors="pt").input_features
        predicted_ids = self.model.generate(input_features, language=origin_language)
        transcription = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)
        return transcription



