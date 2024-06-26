import pyaudiowpatch as pyaudio
import asyncio
import time
import wave


class AudioStreamer:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.format = pyaudio.paInt16
        self.channels = None
        self.rate = None
        self.frames_per_buffer = 512
        self._running = False

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

        self.channels = self.default_speakers['maxInputChannels']
        self.rate = int(self.default_speakers['defaultSampleRate'])
    
    def callback(self, in_data, frame_count, time_info, status):
        self.audio_chunk = in_data
        return (in_data, pyaudio.paContinue)


    async def stream_audio(self):
        self.stream = self.p.open(format=self.format,
                                  channels=self.channels,
                                  rate=self.rate,
                                  input=True,
                                  input_device_index=self.default_speakers['index'],
                                  frames_per_buffer=self.frames_per_buffer,
                                  stream_callback=self.callback)
        self._running = True
        while self._running:
            await asyncio.sleep(0)
            yield self.audio_chunk

    def stop(self):
        self._running = False
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()
    