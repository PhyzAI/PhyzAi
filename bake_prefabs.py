import tempfile
from hashlib import sha256
from re import sub

from rich.progress import track

from OPTIONS import TTS_SRC, TTS
import OPTIONS
from bakery import *

tts_write = TTS.write
DEPENDS_ON_SOURCES = [
    __file__,
    OPTIONS.__file__,
    TTS_SRC
]


def compute_source_hash():
    material = b''
    for file in DEPENDS_ON_SOURCES:
        with open(file, 'r', encoding='utf-8') as f:
            material += sub(r'\s', '', f.read()).encode('utf-8')
    return sha256(material).hexdigest()


HASH = compute_source_hash()


def get_prefab_messages(source_file: Path) -> list[str]:
    with open(source_file, encoding='utf-8') as f:
        all_messages = list(filter(lambda x: x, f.read().splitlines()))
    return all_messages


def bake_one(temporary_file: Path, message: str) -> BakeryRecord:
    tts_write(message, temporary_file)
    with open(temporary_file, 'rb') as f:
        b64 = base64.b64encode(f.read())
    return BakeryRecord(
        text=message,
        base64_audio=b64.decode('utf-8'),
    )


def process_all(source_file: Path, bake_file: Path | None = None):
    if bake_file is None:
        bake_file = source_file.parent / f'baked_{source_file.stem}.json'
    bakery = deserialize_bakery(bake_file)
    if bakery.source_hash != HASH:
        bakery.invalidate_all()
        if bakery.source_hash != '':
            rp(f"[bright_yellow]{source_file} -> {bake_file}: source files changed, re-baking all entries[/]")

    bakery.source_hash = HASH

    messages = set(get_prefab_messages(source_file))
    to_add, removed = bakery.check_and_remove(messages)
    if len(to_add) == 0 and not bakery.is_modified:
        rp(f"[blue]{source_file} -> {bake_file}: up to date[/]")
        return
    if removed > 0:
        rp(f"[red]{source_file}: [bold]{removed} removed[/][/]")
    rp(f"[blue]{source_file}: [bold]{len(to_add)} new[/][/]")

    def save():
        rp(f"[bold green]Saving {bake_file}...[/]")
        with open(bake_file, 'w') as f:
            json.dump(bakery, f, cls=BakerySerializer)
        rp(f"[bold green]All done[/]")

    try:
        with tempfile.TemporaryDirectory() as tempf:
            temp_path = Path(tempf) / "temp.wav"
            for message in track(to_add, "Baking..."):
                baked = bake_one(temp_path, message)
                bakery.add(baked)
    finally:
        save()


if __name__ == '__main__':
    rp(f"[bright_magenta]Current source hash is [bold]{HASH[0:16]}[/][/]")
    process_all(Path("data/apologies.txt"))
    process_all(Path("data/dadJokes.txt"))
    process_all(Path("data/thinking_lines.txt"))
    process_all(Path("data/inappropriate.txt"))
