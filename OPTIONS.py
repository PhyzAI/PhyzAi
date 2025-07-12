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
    rp("[bold blue]Fetch and update prompt...[/]", end='', flush=True)
    resp = requests.get(url)

    # get and parse HTML
    soup = BeautifulSoup(resp.text, 'html.parser')

    text = ""
    for paragraph in soup.select('.wsite-body-section .paragraph'):
        text += paragraph.get_text(separator=' ')
        text += '\n'

    cleaned = re.sub(r'[ \t]{2,}', ' ', text)
    cleaned = re.sub(r'(?:\r?\n){2,}', '\n', cleaned)
    rp("[bold green] ok[/]")
    return cleaned


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
