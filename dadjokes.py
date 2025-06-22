import random
from pathlib import Path

import bakery


class DadJokes:
    def __init__(self, bakery_file="baked_dadJokes.json"):
        self.joke_file = bakery.deserialize_bakery(Path(bakery_file))
        self.jokes = list(self.joke_file.items.values())
        self.just_told_joke = False

    def get_random_joke(self) -> bakery.BakeryRecord | None:
        if not self.jokes:
            return None
        self.just_told_joke = True
        return random.choice(self.jokes)

    def reset_joke_flag(self):
        self.just_told_joke = False

    def is_joke_request(self, text):
        text = text.lower()
        if "tell" in text and ("joke" in text or "another" in text):
            return True
        if text.strip() in ["tell another", "another"]:
            return True
        return False

    def should_tell_another(self, text):
        text = text.lower().strip()
        # Only trigger "tell another" if last was joke
        if text in ["tell another", "another"] and self.just_told_joke:
            return True
        return False
