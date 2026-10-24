import os
import numpy as np
import pyttsx3
import sounddevice as sd
import soundfile as sf
from audiomentations import PitchShift #audiomentations 0.39.0

BYPASS = False

def speak_robot(text, pitch_factor=1.29, carrier_freq=115.0, carrier_amp=0.1):
    engine = pyttsx3.init()
    
    # Optional: Force the specific Windows 11 David voice if needed
    voices = engine.getProperty('voices')
    for voice in voices:
        if "david" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break

    temp_filename = 'temp.wav'
    engine.save_to_file(text, temp_filename)
    engine.runAndWait()
    
    # Read the audio data as float32
    audio, sample_rate = sf.read(temp_filename)
    
    if len(audio.shape) > 1:
        audio = np.mean(audio, axis=1)
        
    # --- NEW PITCH SHIFT METHOD ---
    n_semitones = 12 * np.log2(pitch_factor)

    # Corrected parameter names: min_semitones and max_semitones
    shifter = PitchShift(min_semitones=n_semitones, max_semitones=n_semitones, p=1.0)
    
    pitched_audio = shifter(samples=audio, sample_rate=sample_rate)
    # ------------------------------
    
    # Apply Ring Modulation (using your fine-tuned 115Hz and 0.3 amplitude parameters)
    t = np.arange(len(pitched_audio)) / sample_rate
    carrier = np.sin(2 * np.pi * carrier_freq * t)
    
    # Apply the carrier wave with your custom amplitude tuning
    robot_audio = pitched_audio * (1.0 + carrier_amp * carrier)
    
    # Normalize to prevent digital clipping
    max_val = np.max(np.abs(robot_audio))
    if max_val > 0:
        robot_audio = robot_audio / max_val

    if BYPASS:
         # Output to Windows speakers
         sd.play(audio, sample_rate)
         sd.wait()
    else:
        # Output to Windows speakers
        sd.play(robot_audio, sample_rate)
        sd.wait()
        
    # Clean up file
    if os.path.exists(temp_filename):
        os.remove(temp_filename)

if __name__ == "__main__":
    #speak_robot("PhyzAI system pipeline optimized. Pitch shifting decoupled from time.")
    speak_robot("Ah. I'm PhyzAI, I love solving math and engineering problems")