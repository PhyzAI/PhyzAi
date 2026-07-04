from resemblyzer import VoiceEncoder, preprocess_wav
from pathlib import Path
import numpy as np
import json
import os
import memory_db


#RUNS INDEPENDENT OF PHYZ
class Voice_DB:
    def __init__(self):
        self.file_path = "data/voice_embeds.json"
        self.comparison_threshold = 0.9
        self.embeds = []

    def _load(self): #literally just copied from memory_db.py
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.memories = json.load(f)
        except FileNotFoundError:
            self.memories = []
        except Exception:
            # If file is corrupt, start fresh to avoid crashes.
            self.memories = []


    def _save(self):
        with open(self.file_path, "w", encoding="utf-8") as f: #im just "borrowing" the json snippets from memory_db.py
            json.dump(self.memories, f, ensure_ascii=False, indent=2)


    def add_voice(self, voice_sample_path):
        fpath = Path(voice_sample_path)
        wav = preprocess_wav(fpath)
        encoder = VoiceEncoder()
        embed = encoder.embed_utterance(wav)
        self.embeds.append({"embed": embed, "speaker": Path(voice_sample_path).stem})

        self._save()

    def add_all(self, path="data/known_voices"):
        for file in os.listdir("data/known_voices"):
            self.add_voice(file)

    def find_speaker(self, audio: bytes):
        self._load()
        #embed the just spoken audio
        encoder = VoiceEncoder()
        embed = encoder.embed_utterance(np.array(audio))

        for saved_voice in self.embeds:
            score = memory_db.MemoryDB._cosine_similarity(embed, saved_voice["embed"])
            if score>=self.comparison_threshold:
                return saved_voice["speaker"]

        return None

if __name__ == "__main__":
    vdb = Voice_DB()
    vdb.add_all()
