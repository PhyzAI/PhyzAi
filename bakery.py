import base64
import json
from pathlib import Path

from rich import print as rp


class BakeryRecord:
    def __init__(self, text: str, base64_audio: str):
        self.text = text
        self.base64 = base64_audio
        self.raw = base64.b64decode(base64_audio)

    def serialize(self):
        return {"text": self.text, "base64": self.base64}

    @classmethod
    def deserialize(cls, obj: dict):
        try:
            return cls(
                obj["text"],
                obj["base64"]
            )
        except KeyError:
            rp(f"[red]Encountered error decoding {str(obj)[:64]}..., providing an empty result instead[/]")
            return cls("", "")


class BakeryFile:
    def __init__(self, source_hash: str, items: list[BakeryRecord]):
        self.is_modified = False
        self.source_hash = source_hash
        self.items = {i.text: i for i in items}

    def check_and_remove(self, new_messages: set[str]) -> tuple[set[str], int]:
        known = self.items.keys()
        to_remove = known - new_messages
        if to_remove:
            self.is_modified = True
        for text in to_remove:
            del self.items[text]
        return new_messages - known, len(to_remove)

    def add(self, record: BakeryRecord):
        self.is_modified = True
        self.items[record.text] = record

    def invalidate_all(self):
        self.is_modified = True
        self.items = {}

    def serialize(self):
        return {
            "source_hash": self.source_hash,
            "items": list(self.items.values())
        }

    @classmethod
    def deserialize(cls, obj: dict):
        source_hash = obj["source_hash"]
        items: list[BakeryRecord] = []
        for item in obj["items"]:
            items.append(BakeryRecord.deserialize(item))
        return cls(source_hash, items)

    @classmethod
    def empty(cls):
        obj = cls("", [])
        obj.is_modified = True
        return obj


class BakerySerializer(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, BakeryRecord) or isinstance(o, BakeryFile):
            return o.serialize()
        return super().default(o)


def deserialize_bakery(bake_file: Path) -> BakeryFile:
    if not bake_file.exists():
        return BakeryFile.empty()
    with open(bake_file, encoding='utf-8') as f:
        data = json.load(f)
    return BakeryFile.deserialize(data)
