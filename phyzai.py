from io import BytesIO

import sounddevice as sd
import whisper
import time
import threading
import queue
from scipy.io import wavfile

from apologies import Apologies
from dadjokes import DadJokes
from transcribe2gpt import ask_chatgpt
from transcriber import record_until_silence, transcribe_audio
from tts import speak
from idlechecker import check_idle_and_prompt_chatgpt
from OPTIONS import TTS, prompt


speak = TTS.speak

SYSTEM_PROMPT = prompt

audio_queue = queue.Queue()
last_interaction_time = time.time()



def audio_recorder_loop():
    while True:
        audio = record_until_silence()
        audio_queue.put(audio)

def play_wav(raw: bytes):
    with BytesIO(raw) as filelike:
        samplerate, data = wavfile.read(filelike)
    sd.play(data, samplerate)
    sd.wait()


def main():
    model = whisper.load_model("base")  # Load Whisper model once
    dad_jokes = DadJokes()  # Load jokes once
    apologies = Apologies()  # Load apologies once
    last_idle_response_time = 0  # separate from last user interaction
    IDLE_PROMPT_INTERVAL = 15    # seconds between idle prompts
    global last_interaction_time

    print("PHYZAI is listening... Say 'exit' to quit.")

    recorder_thread = threading.Thread(target=audio_recorder_loop, daemon=True)
    recorder_thread.start()

    while True:
        try:
            # Try to get recorded audio
            audio_bytes = audio_queue.get(timeout=1)  # wait max 1 sec
        except queue.Empty:
            current_time = time.time()
            if current_time - last_interaction_time > 10 and current_time - last_idle_response_time > IDLE_PROMPT_INTERVAL:
                if check_idle_and_prompt_chatgpt(last_interaction_time):
                    last_idle_response_time = current_time
            continue

        
        # except queue.Empty:
        #     # No audio yet, check idle
        #     check_idle_and_prompt_chatgpt(last_interaction_time)
        #     continue

        #audio_bytes = record_until_silence()
        transcription = transcribe_audio(model, audio_bytes)
        print(f"You said: {transcription}")

        normalized = transcription.lower().strip().strip(".!?")

        #############################################################
        # Handle exit command
        #############################################################
        if normalized == "exit":
            print("Goodbye! PHYZAI session ended.")
            speak("goodbye")
            break

        #############################################################
        # Check for joke requests
        #############################################################
        if dad_jokes.should_tell_another(normalized):
            joke = dad_jokes.get_random_joke()
            print(f"PHYZAI: playing {joke.text}")
            play_wav(joke.raw)
            continue
        elif dad_jokes.is_joke_request(normalized) and normalized not in ["tell another", "another"]:
            joke = dad_jokes.get_random_joke()
            print(f"PHYZAI: {joke.text}")
            play_wav(joke.raw)
            continue
        else:
            # Reset joke flag only if input is NOT joke related
            dad_jokes.reset_joke_flag()

        #############################################################
        # Check for apology requests
        #############################################################
        apology_response = apologies.handle_apology_request(transcription)
        if apology_response:
            print(f"PHYZAI: {apology_response.text}")
            play_wav(apology_response.raw)
            continue

        # Otherwise normal GPT response
        response = ask_chatgpt(SYSTEM_PROMPT, transcription)
        if (response):
            last_interaction_time = time.time()
        #speak(response)
        print(f"PHYZAI: {response}")

        if check_idle_and_prompt_chatgpt(last_interaction_time):
            last_interaction_time = time.time()


if __name__ == "__main__":
    main()
