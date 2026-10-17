import os
import numpy as np
import pyttsx3
import sounddevice as sd
import soundfile as sf  # Swapped scipy.io.wavfile for soundfile
from scipy.signal import resample

def pitch_shift(audio, shift_factor):
    num_samples = int(len(audio) / shift_factor)
    resampled = resample(audio, num_samples)
    
    if len(resampled) > len(audio):
        return resampled[:len(audio)]
    else:
        return np.pad(resampled, (0, len(audio) - len(resampled)), 'constant')

def speak_robot(text, pitch_factor=1.22, carrier_freq=115.0, carrier_amp=0.4):
    # Initialize the engine
    engine = pyttsx3.init()

    # Get the current default rate (usually ~200)
    current_rate = engine.getProperty('rate') 
    print(f"Default speaking speed: {current_rate} words per minute")

    # Set a new, slower rate for your robot. 
    # Try somewhere between 130 and 160 for a cold, calculated robot cadence.
    engine.setProperty('rate', 145)
    
    # --- VOICE SELECTION BLOCK ---
    voices = engine.getProperty('voices')
    #for voice in voices:
    #    print(f"Voice: {voice.name}, ID: {voice.id}, Languages: {voice.languages}\n")
    
    # Target common Mac male voices. 
    # 'Alex' is excellent and built-in, but we'll also check for any voice with 'male' or 'Fred'
    selected_voice_id = None
    
    # First preference: Try to find the high-quality 'Alex' voice
    for voice in voices:
        if "ralph" in voice.name.lower():
            selected_voice_id = voice.id
            break
            
    # Second preference: Find any voice flagged as male in its metadata or description
    if not selected_voice_id:
        for voice in voices:
            # Check the language/gender properties if available, or scan the name/age fields
            if hasattr(voice, 'gender') and voice.gender == 'male':
                selected_voice_id = voice.id
                break
            elif "male" in str(voice.languages).lower() or "fred" in voice.name.lower():
                selected_voice_id = voice.id
                break

    # If a male voice was found, tell the engine to use it
    if selected_voice_id:
        engine.setProperty('voice', selected_voice_id)
    else:
        print("Warning: Could not explicitly find a male voice. Using default voice.")
    # ------------------------------






    # We can name it temp.aiff to be honest to macOS, or leave it as temp.wav.
    # sf.read() will autodetect and read it correctly regardless of extension.
    temp_filename = 'temp.wav'
    
    engine.save_to_file(text, temp_filename)
    engine.runAndWait()
    
    # 1. FIX: soundfile automatically detects 'FORM' (AIFF) or 'RIFF' (WAV)
    # It also naturally returns the audio normalized as float32 between -1.0 and 1.0!
    audio, sample_rate = sf.read(temp_filename)
    
    # Handle stereo to mono conversion if Mac outputs 2 channels
    if len(audio.shape) > 1:
        audio = np.mean(audio, axis=1)
        
    # 2. STEP ONE: Pitch Shift
    pitched_audio = pitch_shift(audio, pitch_factor)
    
    # 3. STEP TWO: Ring Modulation
    t = np.arange(len(pitched_audio)) / sample_rate
    carrier = np.sin(2 * np.pi * carrier_freq * t)
    
    robot_audio = pitched_audio * (1.0 + carrier_amp * carrier)
    
    # Normalize to prevent digital clipping
    max_val = np.max(np.abs(robot_audio))
    if max_val > 0:
        robot_audio = robot_audio / max_val
    
    # 4. Play it
    sd.play(robot_audio, sample_rate)
    sd.wait()
    
    # Clean up the temp file
    if os.path.exists(temp_filename):
        os.remove(temp_filename)

if __name__ == "__main__":
    #speak_robot("PhyzAI system online. External mixer bypassed.")
    speak_robot("Ah. I'm PhyzAI, I love solving math and engineering problems")