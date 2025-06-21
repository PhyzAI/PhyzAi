import sounddevice as sd
import webrtcvad
import collections
import wave
import numpy as np

def record_until_silence(sample_rate=16000, frame_duration=30, padding_duration=0.8, vad_aggressiveness=2):
    """
    Records audio from the microphone, starts recording when speech is detected,
    and stops recording shortly after speech ends.

    Returns:
        bytes: The raw audio bytes recorded.
    """
    vad = webrtcvad.Vad(vad_aggressiveness)

    frame_size = int(sample_rate * frame_duration / 1000)  # samples per frame
    padding_frames = int(padding_duration * 1000 / frame_duration)

    stream = sd.InputStream(samplerate=sample_rate, channels=1, dtype='int16')
    stream.start()

    ring_buffer = collections.deque(maxlen=padding_frames)
    triggered = False
    voiced_frames = []

    print("Listening for speech...")

    while True:
        data, overflowed = stream.read(frame_size)
        if overflowed:
            print("Warning: buffer overflow")
        audio_bytes = data.tobytes()

        is_speech = vad.is_speech(audio_bytes, sample_rate)

        print(f'Speaking: {len([f for f, speech in ring_buffer if speech])}')

        if not triggered:
            ring_buffer.append((audio_bytes, is_speech))
            num_voiced = len([f for f, speech in ring_buffer if speech])
            if num_voiced > 0.6 * ring_buffer.maxlen:
                triggered = True
                print("Speech detected, recording...")
                # Add all buffered frames to voiced_frames
                for f, s in ring_buffer:
                    voiced_frames.append(f)
                ring_buffer.clear()
        else:
            voiced_frames.append(audio_bytes)
            ring_buffer.append((audio_bytes, is_speech))
            num_unvoiced = len([f for f, speech in ring_buffer if not speech])
            if num_unvoiced > 0.95 * ring_buffer.maxlen:
                print("Silence detected, stopping recording.")
                break

    stream.stop()

    audio_data = b''.join(voiced_frames)
    return audio_data

def save_wav(filename, audio_data, sample_rate=16000):
    """
    Saves raw audio bytes to a WAV file.
    """
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16 bits = 2 bytes
        wf.setframerate(sample_rate)
        wf.writeframes(audio_data)

def transcribe_audio(model, audio_bytes, sample_rate=16000):
    """
    Transcribe given raw audio bytes using the Whisper model.
    """
    # Save temp file (Whisper loads audio from file)
    temp_filename = "temp_audio.wav"
    save_wav(temp_filename, audio_bytes, sample_rate)

    print("Transcribing...")
    result = model.transcribe(temp_filename)
    return result['text'].strip()
