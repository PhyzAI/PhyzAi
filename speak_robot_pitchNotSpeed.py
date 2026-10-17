import os
import numpy as np
import pyttsx3
import sounddevice as sd
import soundfile as sf
#import librosa  # <-- Added librosa
from audiomentations import PitchShift

def speak_robot(text, pitch_factor=1.23, carrier_freq=115.0, carrier_amp=0.1):
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
    # librosa expects pitch shifts in 'semitones' (half-steps on a piano).
    # To convert your 1.23 multiplier into semitones: 12 * log2(1.23) ≈ 3.58 semitones up.
    n_semitones = 12 * np.log2(pitch_factor)

    shifter = PitchShift(min_semi_tones=n_semitones, max_semi_tones=n_semitones, p=1.0)
    
    # This shifts the pitch up while keeping the EXACT original duration
    #pitched_audio = librosa.effects.pitch_shift(audio, sr=sample_rate, n_steps=n_semitones)
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
    
    # Output to Windows speakers
    sd.play(robot_audio, sample_rate)
    sd.wait()
    
    # Clean up file
    if os.path.exists(temp_filename):
        os.remove(temp_filename)

if __name__ == "__main__":
    speak_robot("PhyzAI system pipeline optimized. Pitch shifting decoupled from time.")