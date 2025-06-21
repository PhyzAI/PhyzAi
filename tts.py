from pathlib import Path

from melo.api import TTS
import sounddevice as sd
from scipy.io import wavfile

speed = 1.0
model = TTS(language='EN', device='auto')
speaker_ids = model.hps.data.spk2id
output_path = 'en-us.wav'


def write(text: str, path: Path | str):
    model.tts_to_file(text, speaker_ids['EN-US'], str(path), speed=speed)


# Placeholder for TTS (Text-to-Speech) functionality
def speak(text):
    write(text, output_path)
    samplerate, data = wavfile.read(output_path)
    sd.play(data, samplerate)
    sd.wait()
