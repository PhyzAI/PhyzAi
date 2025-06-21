import glob
import random

class DadJokes:
    def __init__(self, folder="baked_dadJokes"):
        self.jokes = self.load_jokes(folder)
        self.just_told_joke = False

    def load_jokes(self, folder):
        return glob.glob(f'{folder}/*.wav')

    def get_random_joke(self):
        if not self.jokes:
            return "Sorry, no jokes available!"
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
