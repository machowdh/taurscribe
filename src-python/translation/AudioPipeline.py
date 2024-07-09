from transformers import pipeline


class AudioPipeline:
    
    def __init__(self):
        self.pipe = pipeline("automatic-speech-recognition", model="openai/whisper-tiny")

    def translate(self, audio, language):
        outputs =  self.pipe(audio, max_new_tokens=256, generate_kwargs={"task": "transcribe", "language": language})
        return outputs["text"]
    
    