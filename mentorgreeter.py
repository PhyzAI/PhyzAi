# mentorgreeter.py

import os
import random
import time

MENTOR_FILE_PATH = "seen_mentors.txt"
GREETINGS_FILE_PATH = "data/mentor_greetings.txt"

# Load greetings once
with open(GREETINGS_FILE_PATH, "r", encoding="utf-8") as f:
    GREETINGS = [line.strip() for line in f if line.strip()]

greeted_mentors = {}  # {mentor_name: last_greeted_timestamp}


def check_for_new_mentors_and_greet(speak_fn):
    global greeted_mentors
    current_time = time.time()
    TIME_TO_FORGET = 15  # seconds (adjust as needed)

    if not os.path.exists(MENTOR_FILE_PATH):
        return

    try:
        with open(MENTOR_FILE_PATH, "r", encoding="utf-8") as f:
            current_mentors = set(line.strip() for line in f if line.strip())
    except Exception as e:
        print(f"[ERROR] Reading mentor file: {e}")
        return

    # Greet new or returning mentors
    for name in current_mentors:
        last_greeted = greeted_mentors.get(name, 0)
        if current_time - last_greeted > TIME_TO_FORGET:
            greeting_template = random.choice(GREETINGS)
            greeting = greeting_template.replace("{name}", name).replace("{Mentor}", name)
            print(f"PHYZAI (mentor greet): {greeting}")
            speak_fn(greeting)
            greeted_mentors[name] = current_time

    # Remove mentors who have left the frame (no longer in file)
    previous_mentors = set(greeted_mentors.keys())
    mentors_who_left = previous_mentors - current_mentors
    for name in mentors_who_left:
        del greeted_mentors[name]
