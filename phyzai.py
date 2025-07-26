import queue
import random
import threading
import time
from enum import Enum, auto
from io import BytesIO
from queue import Queue
from typing import Generic, TypeVar

import sounddevice as sd
import whisper
from rich import print as rp
from scipy.io import wavfile

import remote_control
from OPTIONS import prompt, TTS
from actual_chatgpt import ask_chatgpt
from apologies import Apologies
from dadjokes import DadJokes
from idlechecker import check_idle_and_prompt_chatgpt
from mentorgreeter import check_for_new_mentors_and_greet
from thinkingLines import ThinkingLines
from transcriber import record_until_silence, transcribe_audio
# from tts import TTS

speak = TTS.speak

SYSTEM_PROMPT = prompt


class AltResult(Enum):
    cancelled = 0


audio_queue: Queue[bytes | AltResult] = Queue()


class RecordingEvent(Enum):
    START_RECORDING = auto()
    CANCEL_RECORDING = auto()


recording_events: Queue[RecordingEvent] = Queue()

flag_quit = False
flag_cancel_playback = False
flag_hold_record = False

last_interaction_time = time.time()

T = TypeVar("T")


class Box(Generic[T]):
    def __init__(self, initial_value: T):
        self.value = initial_value


def oneshot_record_audio(output_to: Box[bytes]):
    audio = record_until_silence()
    output_to.value = audio


def flush_queue(q: Queue):
    try:
        while True:
            q.get_nowait()
    except queue.Empty:
        pass



def audio_recorder_loop():
    while True:
        if flag_hold_record:
            time.sleep(0.1)
            continue

        # Empty the event queue
        flush_queue(recording_events)

        audio = Box(b'')
        thr = threading.Thread(target=oneshot_record_audio, daemon=True, args=(audio,))
        thr.start()
        is_aborted = False
        # Poll for 'cancel recording' events
        while thr.is_alive():
            try:
                evt = recording_events.get_nowait()
                if evt == RecordingEvent.CANCEL_RECORDING and not is_aborted:
                    audio_queue.put(AltResult.cancelled)
                    is_aborted = True
            except queue.Empty:
                time.sleep(0)  # Yield control elsewhere
        if not is_aborted:
            thr.join()
            audio_queue.put(audio.value)


def audio_manual_loop():
    while True:
        event = recording_events.get()  # blocking
        match event:
            case RecordingEvent.CANCEL_RECORDING:
                continue
            case RecordingEvent.START_RECORDING:
                if flag_hold_record:
                    continue  # Not a good time to record.
                pass  # continues into the below block
            case _:
                continue

        audio = Box(b'')
        thr = threading.Thread(target=oneshot_record_audio, daemon=True, args=(audio,))
        thr.start()
        is_aborted = False

        while thr.is_alive():
            try:
                evt = recording_events.get_nowait()
                if evt == RecordingEvent.CANCEL_RECORDING and not is_aborted:
                    audio_queue.put(AltResult.cancelled)
                    is_aborted = True
            except queue.Empty:
                time.sleep(0)

        if not is_aborted:
            thr.join()
            audio_queue.put(audio.value)

        flush_queue(recording_events)


def rc_event_loop(control_queue: Queue):
    global flag_quit, flag_cancel_playback
    while True:
        # blocks until we get something
        next_input: bytes = control_queue.get()
        rp(f'[bright_blue][bold]command[/] {next_input}[/]')
        # since 3.10
        match next_input:
            case b'3':  # cancel response (inappropriate question)
                recording_events.put(RecordingEvent.CANCEL_RECORDING)
                flag_cancel_playback = True
            case b'4':  # start listening
                recording_events.put(RecordingEvent.START_RECORDING)
            case b'5':  # quit
                flag_quit = True
                return
            case b'6':  # change provider
                # TODO
                ...
            case _:
                rp(f'[red]rc: not sure what to do with {next_input} (0x{next_input[0]:02x})[/]')


def play_wav(raw: bytes):
    with BytesIO(raw) as filelike:
        samplerate, data = wavfile.read(filelike)
    sd.play(data, samplerate)
    sd.wait()


def main():
    global flag_cancel_playback, flag_quit, flag_hold_record
    model = whisper.load_model("base")  # Load Whisper model once
    dad_jokes = DadJokes()  # Load jokes once
    apologies = Apologies()  # Load apologies once
    thinking_lines = ThinkingLines()
    control_queue = remote_control.start_auto()
    last_idle_response_time = 0  # separate from last user interaction
    IDLE_PROMPT_INTERVAL = 15  # seconds between idle prompts
    global last_interaction_time

    print("PHYZAI is listening... Say 'exit' to quit.")

    recorder_thread = threading.Thread(target=audio_manual_loop, daemon=True)
    recorder_thread.start()
    rc_thread = threading.Thread(target=rc_event_loop, daemon=True, args=(control_queue,))
    rc_thread.start()

    while True:
        try:
            audio_bytes = audio_queue.get(timeout=1)  # wait max 1 sec
        except queue.Empty:
            flag_cancel_playback = False
            current_time = time.time()

            if flag_quit:
                print("ending session (command)")
                speak("goodbye")
                return

            # check to see if there are any new mentors in screen
            if audio_queue.empty():  # or similar condition to ensure Phyz is not busy
                check_for_new_mentors_and_greet(speak)

            response, last_idle_response_time = check_idle_and_prompt_chatgpt(
                last_interaction_time, last_idle_response_time
            )
            if response:
                print(f"PHYZAI (idle): {response}")
                speak(response)
            continue

        # It might have failed...
        if audio_bytes == AltResult.cancelled:
            rp(f"[red][bold]aborted[/] (mod)[/]")
            continue

        flag_hold_record = True

        # except queue.Empty:
        #     # No audio yet, check idle
        #     check_idle_and_prompt_chatgpt(last_interaction_time)
        #     continue

        # audio_bytes = record_until_silence()
        transcription = transcribe_audio(model, audio_bytes)
        rp(f"[cyan][bold]You said:[/] {transcription}[/]")

        if flag_cancel_playback:
            continue

        normalized = transcription.lower().strip().strip(".!?")

        #############################################################
        # Handle exit command
        #############################################################
        if normalized == "exit" or flag_quit:
            print("Goodbye! PHYZAI session ended.")
            speak("goodbye")
            return

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
        rp(f"PHYZAI: [bold bright_green]saying[/] [green]llm[/] {response}")

        if flag_cancel_playback:
            continue

        speak(response)

        flag_hold_record = False

        if check_idle_and_prompt_chatgpt(last_interaction_time, last_idle_response_time):
            last_interaction_time = time.time()


if __name__ == "__main__":
    main()
