import random
from pathlib import Path

import bakery


class ThinkingLines:
    def __init__(self, bakery_file="data/baked_thinkingLines.json"):
        self.think_file = bakery.deserialize_bakery(Path(bakery_file))
        self.think_lines = list(self.think_file.items.values())

    def get_random_think_line(self) -> bakery.BakeryRecord | None:
        if not self.think_lines:
            return None
        return random.choice(self.think_lines)

