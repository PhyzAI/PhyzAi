from pathlib import Path

import torch

import torchaudio
import torch.nn.functional as F
from scipy.spatial.distance import cdist
from sklearn.svm import SVC
from speechbrain.inference.speaker import EncoderClassifier

import numpy as np
import json
import os

# from sklearn import svm

import memory_db
from transcriber import record_until_silence, save_wav
# from sklearn.svm import SVC



#RUNS INDEPENDENT OF PHYZ
class Voice_DB:
    def __init__(self):
        self.file_path = "data/voice_embeds.json"
        self.comparison_threshold = 0.60
        self.embeds = []
        self.voice_checking_priority = ["Bahadir", "LeAnn", "Keith"]
        self._load()

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


    def _save(self, debug=False):
        if debug: print(self.embeds)

        with open(self.file_path, "w", encoding="utf-8") as f: #im just "borrowing" the json snippets from memory_db.py
            json.dump(self.embeds, f, ensure_ascii=False, indent=2)


    def add_all(self, path="data/known_voices/MISC"):
        classifier = EncoderClassifier.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb"
        )

        user_embeds = []
        directory = os.listdir(path)
        directory.sort()
        for file in directory:
            voice_sample_path = path + "/" + file # step 1, generate embedding per user sample
            print(f"Loading from {voice_sample_path}")
            signal, fs = torchaudio.load(voice_sample_path)
            embedding = classifier.encode_batch(signal)
            # print(embedding)
            user_embeds.append(embedding)

        final_embed = torch.stack(user_embeds, dim=0).mean(dim=0)
        self.embeds.append({"embed": final_embed.tolist(), "speaker": Path(path).name})
        print(f"generated embeddings for user: {Path(path).name}")
        self._save()


    def find_speaker(self, audio: bytes):
        if audio is None: return None # if timeout is hit
        #embed the just spoken audio

        wave_array = np.frombuffer(audio, dtype=np.int16)
        if wave_array.dtype == np.int16:
            wave_array = wave_array.astype(np.float32) / 32768.0 #converts the pcm wave data to a float32 for resemblyzer
        wave_tensor = torch.from_numpy(wave_array).float() # convert from numpy

        classifier = EncoderClassifier.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb" #ECAPA-TDNN based encoder
        )
        embedding = classifier.encode_batch(wave_tensor).squeeze()
        current = torch.as_tensor(embedding, dtype=torch.float32).squeeze()

        relevant = [x for x in self.embeds if x["speaker"] in self.voice_checking_priority]
        rest = [x for x in self.embeds if x["speaker"] not in self.voice_checking_priority]

        new_order = relevant + rest

        for user in new_order:
            #Checks Bahadir first and then the rest of the priority then everyone else
            saved = torch.as_tensor(user["embed"], dtype=torch.float32).squeeze()
            score = F.cosine_similarity(saved, current, dim=0).item()
            print(f"Attempted Detection: Score {score}, User {user['speaker']}")
            if score >= self.comparison_threshold:
                print(f"User: {user['speaker']} Score: {score}")
                return user["speaker"]

        return "Unknown User"

    def collect_voices(self, username, training_count, gen_embeds=False): # its best to collect voices using different mics, and different angles - see voice_training.txt for training lines
        for i in range(training_count):  # x voice samples
            print(f"Recording for sample {i}")
            audio = record_until_silence()
            filename = f"data/known_voices/{username}/Sample{i:02d}.wav"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            save_wav(filename=filename,
                     audio_data=audio)  # 2 digit number format, change the user for who you're recording for
            print(f"Saved for sample {i}")

        if gen_embeds:
            print(f"Generating the embeddings for: {username}")
            self.add_all(path=f"data/known_voices/{username}")


if __name__ == "__main__":
    vdb = Voice_DB()
    # vdb.collect_voices("Bahadir", 10, gen_embeds=True)
    # vdb.add_all("data/known_voices/Ayaan")

    audio = record_until_silence()  # seconds
    voice_db = Voice_DB()
    print(voice_db.find_speaker(audio))  # print the speaker