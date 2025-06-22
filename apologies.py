import random
from pathlib import Path

import bakery


class Apologies:
    def __init__(self, bakery_file="baked_apologies.json"):
        self.apologies_file = bakery.deserialize_bakery(Path(bakery_file))
        self.apologies = list(self.apologies_file.items.values())

    def get_random_apology(self) -> bakery.BakeryRecord | None:
        if not self.apologies:
            return None
        return random.choice(self.apologies)

    def handle_apology_request(self, text) -> bakery.BakeryRecord | None:
        normalized = text.lower().strip(".!? ")

        # Very simple keyword-based trigger
        if any(word in normalized for word in ["say sorry", "apologize", "apologies"]):
            return self.get_random_apology()

        return None
