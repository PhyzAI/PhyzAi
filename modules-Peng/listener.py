import io
from datetime import datetime, timedelta
from queue import Queue

import speech_recognition as sr

# Speech Recognition Parameters
ENERGY_THRESHOLD = 1000  # Energy level for mic to detect
PHRASE_TIMEOUT = 3.0  # Space between recordings for sepating phrases
RECORD_TIMEOUT = 5

class Listener:
    def __init__(self):
        self.listener_handle = None
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = ENERGY_THRESHOLD
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.pause_threshold = 1
        self.last_sample = bytes()
        self.phrase_time = datetime.utcnow()
        self.phrase_timeout = PHRASE_TIMEOUT
        self.phrase_complete = False
        # Thread safe Queue for passing data from the threaded recording callback.
        self.data_queue = Queue()
        self.mic_dev_index = 2
        self.source = sr.Microphone(sample_rate=16000, device_index=self.mic_dev_index)

    def listen(self):
        if not self.listener_handle:
            print("listening")
            while True:
                with self.source:
                    self.recognizer.adjust_for_ambient_noise(self.source)
                    audio = self.recognizer.listen(self.source, phrase_time_limit=RECORD_TIMEOUT)
                    if audio:
                        data = audio.get_raw_data()
                        self.data_queue.put(data)
                        break

    def record_callback(self, _, audio: sr.AudioData) -> None:
        # Grab the raw bytes and push it into the thread safe queue.
        data = audio.get_raw_data()
        self.data_queue.put(data)

    def speech_waiting(self):
        return not self.data_queue.empty()

    def get_speech(self):
        if self.speech_waiting():
            return self.data_queue.get()
        return None

    def get_audio_data(self):
        now = datetime.utcnow()
        if self.speech_waiting():
            self.phrase_complete = False
            if self.phrase_time and now - self.phrase_time > timedelta(
                seconds=self.phrase_timeout
            ):
                self.last_sample = bytes()
                self.phrase_complete = True
            self.phrase_time = now

            # Concatenate our current audio data with the latest audio data.
            while self.speech_waiting():
                data = self.get_speech()
                self.last_sample += data

            # Use AudioData to convert the raw data to wav data.
            audio_data = sr.AudioData(
                self.last_sample, self.source.SAMPLE_RATE, self.source.SAMPLE_WIDTH
            )
            wav_data = io.BytesIO(audio_data.get_wav_data())
            return wav_data

        return None