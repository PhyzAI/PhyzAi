from importlib import import_module
from pathlib import Path
from typing import Protocol, cast


class TTSProvider(Protocol):
    def write(self, text: str, path: Path | str):
        ...

    def speak(self, text: str):
        ...


TTS: TTSProvider = cast(TTSProvider, import_module("ttsx"))
TTS_SRC = TTS.__file__
