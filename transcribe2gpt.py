import os
import wave
import tempfile
import collections
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
import whisper
import webrtcvad
from openai import OpenAI

# Load OpenAI client (replace with your actual key or use .env file)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or "sk-your-api-key")

# Audio recording settings
RATE = 16000
CHANNELS = 1
FRAME_DURATION_MS = 30
FRAME_SIZE = int(RATE * FRAME_DURATION_MS / 1000)
vad = webrtcvad.Vad(2)

def detect_speech():
    print("Listening for speech...")
    buffer = collections.deque(maxlen=int(300 / FRAME_DURATION_MS))
    voiced_frames = []
    recording = False

    def callback(indata, frames, time, status):
        nonlocal recording
        pcm_data = indata.copy().tobytes()
        if vad.is_speech(pcm_data, RATE):
            buffer.append((pcm_data, True))
        else:
            buffer.append((pcm_data, False))

        if not recording:
            if sum(1 for _, speech in buffer if speech) > 0.8 * buffer.maxlen:
                print("Speech detected. Recording...")
                voiced_frames.extend([f for f, _ in buffer])
                buffer.clear()
                recording = True
        elif recording:
            voiced_frames.append(pcm_data)
            if sum(1 for _, speech in buffer if not speech) > 0.9 * buffer.maxlen:
                raise sd.CallbackStop

    with sd.InputStream(samplerate=RATE, channels=CHANNELS, dtype='int16', callback=callback, blocksize=FRAME_SIZE):
        try:
            sd.sleep(10000)  # 10-second timeout fallback
        except sd.CallbackStop:
            pass

    return b''.join(voiced_frames)

def save_audio(wav_bytes, filename):
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(RATE)
        wf.writeframes(wav_bytes)

def transcribe(audio_path):
    print("Transcribing...")
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    print("Transcript:", result['text'])
    return result['text']

def ask_chatgpt(prompt, user_input):
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_input}
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # or "gpt-4"
        messages=messages
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    # Record with voice activation
    audio_data = detect_speech()

    # Save audio to temporary WAV file
    fd, tmpfile_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    save_audio(audio_data, tmpfile_path)

    # Transcribe with Whisper
    transcription = transcribe(tmpfile_path)

    # Delete temp file
    os.remove(tmpfile_path)

    # Get GPT response
    system_prompt = "You are a helpful and concise assistant."
    response = ask_chatgpt(system_prompt, transcription)

    print("\nChatGPT Response:\n" + response)
