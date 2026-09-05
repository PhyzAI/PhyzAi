import time
import sounddevice as sd
import collections
import wave
import numpy as np
import random
# import winsound
import os
import webrtcvad    
import collections

#Bahadir: original vad_aggressiveness was 2
def record_until_silence(sample_rate=16000, frame_duration=30, padding_duration=0.8, vad_aggressiveness=3, timeout=None):
    """
    Records audio from the microphone, starts recording when speech is detected,
    and stops recording shortly after speech ends.

    Parameters:
        sample_rate (int): sample rate for the input stream
        frame_duration (int): duration of a frame in ms used by VAD
        padding_duration (float): seconds of padding used to smooth start/stop
        vad_aggressiveness (int): VAD aggressiveness level (0-3)
        timeout (float|None): maximum number of seconds to wait before returning
            If the timeout expires before speech/silence are detected the
audio captured so far (which may be empty) is returned.

    Returns:
        bytes: The raw audio bytes recorded (may be empty on timeout).
    """
    vad = webrtcvad.Vad(vad_aggressiveness)
    frame_size = int(sample_rate * frame_duration / 1000)
    padding_frames = int(padding_duration * 1000 / frame_duration)
    ring_buffer = collections.deque(maxlen=padding_frames)
    triggered = False
    voiced_frames = []

    frequency = random.randint(400, 1000) # Set Frequency
    duration = 300 # Set Duration To 1000 ms == 1 second

    if os.getenv("COMPUTERNAME") == "PHYZ":
        import winsound
        winsound.Beep(frequency, duration)
    elif os.environ.get("COMPUTERNAME") == "AYAANMAC":
        os.system('afplay /System/Library/Sounds/Glass.aiff')

    stream = sd.InputStream(samplerate=sample_rate, channels=1, dtype='int16')
    start_time = time.time()

    try:
        stream.start()
        print("Listening for speech...")

        while True:
            # check timeout at top of loop so we don't hang forever
            if timeout is not None and (time.time() - start_time) > timeout:
                print(", returning audio captured so far.")
                break

            try:
                data, overflowed = stream.read(frame_size)
                if overflowed:
                    print("Warning: buffer overflow")
                audio_bytes = data.tobytes()
                is_speech = vad.is_speech(audio_bytes, sample_rate)

                if not triggered:
                    ring_buffer.append((audio_bytes, is_speech))
                    num_voiced = len([f for f, speech in ring_buffer if speech])
                    #Bahadir: original threshold was 0.9
                    if num_voiced > 0.99 * ring_buffer.maxlen:
                        triggered = True
                        print("Speech detected, recording...")
                        #write into file to tell phyz to look at mic
                        with open("transcribe_status.txt", "w", encoding="utf-8") as f:
                            f.write("recording")
                        for f, s in ring_buffer:
                            voiced_frames.append(f)
                        ring_buffer.clear()
                else:
                    voiced_frames.append(audio_bytes)
                    ring_buffer.append((audio_bytes, is_speech))
                    num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                    #Bahadir: original threshold was 0.95
                    if num_unvoiced > 0.99 * ring_buffer.maxlen:
                        print("Silence detected, stopping recording.")
                        #write into file to tell phyz to look away from mic
                        open("transcribe_status.txt", "w", encoding="utf-8").close()
                        break
            except Exception as e:
                print(f"[Stream read error] {e}")
                break

    finally:
        stream.stop()
        stream.close()
    
    return b''.join(voiced_frames)

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
