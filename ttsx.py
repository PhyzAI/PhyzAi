import os
import time
from pathlib import Path

import pyttsx3

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


def speak(text: str):
    # bahadir addition three lines below
    with open("speak_status.txt", "r") as f:
        status = f.read().strip().lower()
        if status != "speaking":
            with open("speak_status.txt", "w", encoding="utf-8") as f:
                f.write("speaking")
                #print("Bahadir Debug actually speaking")



    engine.say(text)
    engine.runAndWait()
    open("speak_status.txt", "w", encoding="utf-8").close()
    #print("Bahadir Debug actually speaking")

    # engine.stop()
