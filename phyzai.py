from io import BytesIO

import sounddevice as sd
import whisper
import time
import threading
import queue
import random
from scipy.io import wavfile

import remote_control
from apologies import Apologies
from dadjokes import DadJokes
from thinkingLines import ThinkingLines
from actual_chatgpt import ask_chatgpt
from transcriber import record_until_silence, transcribe_audio

from idlechecker import check_idle_and_prompt_chatgpt
from OPTIONS import TTS, prompt
from OPTIONS import prompt#, TTS
from tts import TTS
from mentorgreeter import check_for_new_mentors_and_greet
from rich import print as rp


speak = TTS.speak
speak = TTS().speak

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
    thinking_lines = ThinkingLines()
    control_queue = remote_control.start_auto()
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

            #check to see if there are any new mentors in screen
            if audio_queue.empty():  # or similar condition to ensure Phyz is not busy
                check_for_new_mentors_and_greet(speak)


            response, last_idle_response_time = check_idle_and_prompt_chatgpt(
                last_interaction_time, last_idle_response_time
            )
            if response:
                print(f"PHYZAI (idle): {response}")
                speak(response)
            continue



        # except queue.Empty:
        #     # No audio yet, check idle
        #     check_idle_and_prompt_chatgpt(last_interaction_time)
        #     continue

        #audio_bytes = record_until_silence()
        transcription = transcribe_audio(model, audio_bytes)
        rp(f"[cyan][bold]You said:[/] {transcription}[/]")

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
            rp(f"PHYZAI: [bold bright_green]playing[/] [yellow]joke[/] {joke}")
            speak(joke)
            continue
        elif dad_jokes.is_joke_request(normalized) and normalized not in ["tell another", "another"]:
            joke = dad_jokes.get_random_joke()
            rp(f"PHYZAI: [bold bright_green]playing[/] [yellow]joke[/] {joke}")
            speak(joke)
            continue
        else:
            # Reset joke flag only if input is NOT joke related
            dad_jokes.reset_joke_flag()

        #############################################################
        # Check for apology requests
        #############################################################
        apology_response = apologies.handle_apology_request(transcription)
        if apology_response:
            rp(f"PHYZAI: [bold bright_green]playing[/] [red]apology[/] {apology_response.text}")
            play_wav(apology_response.raw)
            continue

        # Say thinking line while PHYZ figures out what its saying and renders it
        if random.random() < 0.5:
            thinking = thinking_lines.get_random_think_line()
            if thinking:
                print(f"PHYZAI (thinking): {thinking.text}")
                play_wav(thinking.raw)


        # Otherwise normal GPT response
        response = ask_chatgpt(SYSTEM_PROMPT, transcription)
        if (response):
            last_interaction_time = time.time()
        #speak(response)
        rp(f"PHYZAI: [bold bright_green]saying[/] [green]llm[/] {response}")
        speak(response)

        if check_idle_and_prompt_chatgpt(last_interaction_time, last_idle_response_time):
            last_interaction_time = time.time()


if __name__ == "__main__":
    main()