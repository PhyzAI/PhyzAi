import glob
import random

class Apologies:
    def __init__(self, folder="baked_apologies"):
        self.apologies = self.load_apologies(folder)

    def load_apologies(self, folder):
        return glob.glob(f'{folder}/*.wav')

    def get_random_apology(self):
        if not self.apologies:
            return "I'm really sorry, but I don't have any apologies right now!"
        return random.choice(self.apologies)

    def handle_apology_request(self, text):
        normalized = text.lower().strip(".!? ")

        # Very simple keyword-based trigger
        if any(word in normalized for word in ["say sorry", "apologize", "apologies"]):
            return self.get_random_apology()

        return None
