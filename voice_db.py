import sys

from resemblyzer import VoiceEncoder, preprocess_wav
from pathlib import Path
import numpy as np
import json
import os

from sklearn import svm

import memory_db
from transcriber import record_until_silence
from sklearn.svm import SVC



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
                self.embeds = json.load(f)
        except FileNotFoundError:
            self.embeds = []
        except Exception:
            # If file is corrupt, start fresh to avoid crashes.
            self.embeds = []


    def _save(self):
        print(self.embeds)
        with open(self.file_path, "w", encoding="utf-8") as f: #im just "borrowing" the json snippets from memory_db.py
            json.dump(self.embeds, f, ensure_ascii=False, indent=2)


    def add_voice(self, voice_sample_path, subindex=0):

        print(voice_sample_path)
        print(subindex)
        fpath = Path(voice_sample_path)
        wav = preprocess_wav(fpath)
        encoder = VoiceEncoder()
        embed = encoder.embed_utterance(wav)
        #you cant json serialize a numpy array
        self.embeds[subindex].append({"embed": embed.tolist(), "speaker": Path(voice_sample_path).stem})
        self._save()

    def add_all(self, path="data/known_voices"):
        subindex = 0
        for dir in os.listdir(path):
            self.embeds.append([])
            directory = os.listdir(path + "/" + dir)
            directory.sort()
            for file in directory:
                self.add_voice(path + "/" + dir + "/" + file, subindex)
            subindex+=1


    def find_speaker(self, audio: bytes):
        self._load()
        #embed the just spoken audio
        encoder = VoiceEncoder()
        wav = preprocess_wav(np.frombuffer(audio, dtype=np.int16))
        embed = encoder.embed_utterance(wav)

        for user in self.embeds:
            self.svm(user, embed)

        return None

    def svm(self, current, audio2check):
        # X_train: Matrix of embeddings from your enrolled users + background "imposter" voices
        # y_train: Labels corresponding to the speaker IDs
        X_train = np.array([current[0]["embed"], current[1]["embed"], current[2]["embed"], current[3]["embed"], current[4]["embed"]])
        y_train = np.array([1, 1, 1, 0, 0])  # 1 = Target User, 0 = Someone Else
        # these are pre sorted now

        # Train a Linear SVM with probability outputs enabled
        clf = SVC(kernel='linear', probability=True)
        clf.fit(X_train, y_train)

        # Test a completely new embedding vector
        # predict_proba returns [Probability of being an imposter, Probability of being Target]
        confidence_scores = clf.predict_proba([audio2check])[0]
        print(f"Confidence that this is the target speaker: {confidence_scores[1] * 100:.2f}%")


if __name__ == "__main__":
    # vdb = Voice_DB()
    # vdb.add_all()

    audio = record_until_silence(timeout=20)  # seconds
    voice_db = Voice_DB()
    print(voice_db.find_speaker(audio))  # print the speaker