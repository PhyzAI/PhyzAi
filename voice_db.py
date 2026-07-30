import sys
from email.mime import audio

from resemblyzer import VoiceEncoder, preprocess_wav
from pathlib import Path
import numpy as np
import json
import os

from sklearn import svm

import memory_db
from transcriber import record_until_silence, save_wav
from sklearn.svm import SVC



#RUNS INDEPENDENT OF PHYZ
class Voice_DB:
    def __init__(self):
        self.file_path = "data/voice_embeds.json"
        self.comparison_threshold = 0.70
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


    def _save(self, debug=False):
        if debug: print(self.embeds)

        with open(self.file_path, "w", encoding="utf-8") as f: #im just "borrowing" the json snippets from memory_db.py
            json.dump(self.embeds, f, ensure_ascii=False, indent=2)


    # def add_voice(self, voice_sample_path, subindex=0):
    #
    #     print(voice_sample_path)
    #     print(subindex)
    #     fpath = Path(voice_sample_path)
    #     wav = preprocess_wav(fpath)
    #     encoder = VoiceEncoder()
    #     embed = encoder.embed_utterance(wav)
    #     #you cant json serialize a numpy array
    #     self.embeds[subindex].append({"embed": embed.tolist(), "speaker": Path(voice_sample_path).stem})
    #     self._save()

    def add_all(self, path="data/known_voices"):
        for dir in os.listdir(path):
            directory = os.listdir(path + "/" + dir)
            directory.sort()
            user_embeds = []
            for file in directory:
                voice_sample_path = path + "/" + dir + "/" + file # step 1, generate embedding per user sample
                fpath = Path(voice_sample_path)

                wav = preprocess_wav(fpath)
                encoder = VoiceEncoder()
                embed = encoder.embed_utterance(wav)

                user_embeds.append(embed)

            final_embed = np.mean(np.stack(user_embeds, axis=0), axis=0)
            self.embeds.append({"embed": final_embed.tolist(), "speaker": dir})
            print(f"generated embeddings for user: {dir}")
        self._save()
        print("generated all embeddings")



    def find_speaker(self, audio: bytes):
        if audio is None: return None # if timeout is hit
        self._load()
        #embed the just spoken audio
        encoder = VoiceEncoder()
        wave_array = np.frombuffer(audio, dtype=np.int16)

        if wave_array.dtype == np.int16:
            wave_array = wave_array.astype(np.float32) / 32768.0 #converts the pcm wave data to a float32 for resemblyzer

        wav = preprocess_wav(wave_array, source_sr=16000)
        embed = encoder.embed_utterance(wav)

        for user in self.embeds:
            score = memory_db.MemoryDB._cosine_similarity(user["embed"], embed)
            print(f"Score: {score}")
            if score >= self.comparison_threshold:
                return user["speaker"]
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
    # vdb.add_all()

    # audio = record_until_silence()  # seconds
    # voice_db = Voice_DB()
    # print(voice_db.find_speaker(audio))  # print the speaker