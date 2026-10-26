USE_SPEAK_ROBOT = True # Use software voice-changing instead of HW voice-changer box
DONT_SPEAK_IF_LISTENING = True # If Phyz is listening, don't speak (to avoid interrupting)
DONT_SPEAK_RETRIES = 5
DONT_SPEAK_RETRY_DELAY = 0.5  # seconds

import os
import time
from pathlib import Path

import pyttsx3

# This is how we can modify the speech in software instead of the external hw box.
from speak_robot_pitchNotSpeed import speak_robot # Import the speak_robot function from the other file
import PhyzShared


engine = pyttsx3.init()
engine.setProperty('rate', 200)
engine.setProperty('volume', 1)


def write(text: str, path: Path | str):
    print(f"{text}")
    if path.exists():
        os.remove(path)
    engine.save_to_file(text, str(path))
    engine.runAndWait()
    while not path.exists():
        print(f"waiting for {path}")
        time.sleep(0.1)


def _execute_speech(text: str, useSpeakRobot: bool):
    """Helper function to manage speaking state safely and execute the speech."""
    PhyzShared.set_speaking_status(True)
    try:
        if useSpeakRobot:
            speak_robot(text)   # note, the wait is included
        else:
            engine.say(text)
            engine.runAndWait()
    finally:
        PhyzShared.set_speaking_status(False)


def speak(text: str, useSpeakRobot: bool = False):
    if DONT_SPEAK_IF_LISTENING:
        for _ in range(DONT_SPEAK_RETRIES):
            if not PhyzShared.get_listening_status():
                break
            time.sleep(DONT_SPEAK_RETRY_DELAY)

        if PhyzShared.get_listening_status():
            return
    _execute_speech(text, useSpeakRobot=USE_SPEAK_ROBOT)
