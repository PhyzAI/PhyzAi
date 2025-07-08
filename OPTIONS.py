import re
from importlib import import_module
from pathlib import Path
from typing import Protocol, cast
from rich import print as rp

import requests
from bs4 import BeautifulSoup


class TTSProvider(Protocol):
    def write(self, text: str, path: Path | str):
        ...

    def speak(self, text: str):
        ...


TTS: TTSProvider = cast(TTSProvider, import_module("ttsx"))
TTS_SRC = TTS.__file__

url = "https://www.rise4steam.org/the-blarts.html"
with open('prompt_base.txt', 'r', encoding='utf-8') as f:
    prompt = f.read()


def fetch_prompt():
    rp("[bold blue]Fetch and update prompt...[/]")
    resp = requests.get(url)

    # get and parse HTML
    soup = BeautifulSoup(resp.text, 'html.parser')

    text = soup.get_text()

    clean = ' '.join(text.split())

    matcher = re.search(
        r'Meet the Blarts([\w\W]*?)Get ready to explore the wonders of science with Thunk, Spin, Click, and Clack!',
        clean
    )
    rp("[bold blue]...done[/]")
    return matcher.group(1)


try:
    prompt += '\n'
    prompt += fetch_prompt()
except Exception as e:
    print(e)
    rp("[blue]Using prompt from cache[/]")
    with open('prompt_cache.txt', 'r', encoding='utf-8') as f:
        prompt = f.read()
else:
    with open('prompt_cache.txt', 'w', encoding='utf-8') as f:
        f.write(prompt)

with open('prompt_override.txt', 'r', encoding='utf-8') as f:
    prompt_override = f.read()
