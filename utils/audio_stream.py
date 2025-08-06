import sounddevice as sd
import numpy as np

class AudioStream:
    def __init__(self, device, samplerate=44100, channels=6, chunk_duration=0.1):
        self.device = device
        self.samplerate = samplerate
        self.channels = channels
        self.chunk_duration = chunk_duration
        self.chunk_samples = int(samplerate * chunk_duration)

    def get_audio_chunk(self):
        recording = sd.rec(self.chunk_samples, samplerate=self.samplerate,
                           channels=self.channels, device=self.device)
        sd.wait()
        return recording.T  # 转置为 (channels, samples)
