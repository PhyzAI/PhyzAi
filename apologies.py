import random

class Apologies:
    def __init__(self, filename="apologies.txt"):
        self.apologies = self.load_apologies(filename)

    def load_apologies(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]

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
