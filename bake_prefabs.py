import shutil
from pathlib import Path
from tts import write as tts_write
from rich.progress import track


def get_prefab_messages(source_file: Path) -> list[str]:
    with open(source_file, encoding='utf-8') as f:
        all_messages = list(filter(lambda x: x, f.read().splitlines()))
    return all_messages


def bake(render_dir: Path, messages: list[str]):
    shutil.rmtree(render_dir, ignore_errors=True)
    render_dir.mkdir(parents=True, exist_ok=True)
    for i, msg in enumerate(track(messages, f'{render_dir}: {len(messages)} total')):
        tts_write(msg, render_dir / f'{i}.wav')


def process_all(source_file: Path):
    messages = get_prefab_messages(source_file)
    name = source_file.stem
    out = Path(f"baked_{name}/")
    bake(out, messages)


if __name__ == '__main__':
    process_all(Path("apologies.txt"))
    process_all(Path("dadJokes.txt"))
