import numpy as np
import sounddevice as sd
from scipy.signal import resample
from TTS.api import TTS as CoquiTTS

class TTS:
    def __init__(self, model_name="tts_models/en/ljspeech/glow-tts"):
        print("[TTS] Loading model...")
        self.tts = CoquiTTS(model_name)
        self.original_samplerate = 22050  # default Coqui sample rate
        self.pitch_factor = 1.00  # <--- Lower this to make it deeper (e.g. 0.8 = lower pitch)

    def speak(self, text):
        print(f"[TTS] Speaking: {text}")
        try:
            # Generate audio
            wav = self.tts.tts(text)

            # Pitch down by resampling
            new_length = int(len(wav) / self.pitch_factor)
            pitched_wav = resample(wav, new_length)

            # Adjust samplerate accordingly
            new_samplerate = int(self.original_samplerate * self.pitch_factor)

            # Play pitched audio
            sd.play(pitched_wav, new_samplerate)
            sd.wait()
        except Exception as e:
            print(f"[TTS ERROR] Failed to synthesize: {e}")
