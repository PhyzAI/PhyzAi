from io import BytesIO

import sounddevice as sd
import whisper
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import queue
import random
from scipy.io import wavfile
import os

from sympy.parsing.sym_expr import cin
from sympy.physics.quantum.gate import normalized

import remote_control
from actual_SLM import should_remember
from apologies import Apologies
from dadjokes import DadJokes
from debug_config import DEBUG
from thinkingLines import ThinkingLines
from actual_chatgpt import ask_chatgpt
from actual_gemini import ask_gemini
from actual_claude import ask_claude
from memory_db import MemoryDB
from transcriber import record_until_silence, transcribe_audio

from idlechecker import check_idle_and_prompt_chatgpt
from OPTIONS import TTS, prompt
from OPTIONS import prompt, TTS
#from tts import TTS
from ttsx import speak as ttsx_speak
from mentorgreeter import check_for_new_mentors_and_greet
from rich import print as rp
import serial
from datetime import datetime

from voice_db import Voice_DB

# Init communication with Arduino (optional: runs without serial if COM4 unavailable)
LOW_COMMAND = bytes('l', "utf-8")
HIGH_COMMAND = bytes('h', "utf-8")
serialObj = None
try:
    #COM4 on Phyz and COM3 on Bahadir's laptop
    if os.environ.get("COMPUTERNAME") == "BAHADIRGRAM":
        serialObj = serial.Serial('COM3', 9600, bytesize=8, parity='N', stopbits=1, timeout=None)
    else:
        serialObj = serial.Serial('COM4', 9600, bytesize=8, parity='N', stopbits=1, timeout=None)

    serialObj.write(LOW_COMMAND)
    serialObj.flush()
    time.sleep(1)
except serial.SerialException as e:
    rp(f"[yellow]Serial port COM4 not available: {e}[/yellow]")
    rp("[yellow]Running without Arduino. Check Device Manager for the correct COM port.[/yellow]")

# For the continuous listening mode, we need True for listeningmode. For button activated mode
# switch to False.
listeningmode = True

speak = ttsx_speak
# speak = TTS().speak

audio_queue = queue.Queue()
last_interaction_time = time.time()

#Create space to store memory of responses
conversation_history = []
# Keep track of the last Q/A pair for "remember that" commands
last_user_query: str | None = None
last_assistant_response: str | None = None

#System Prompt Definition
SYSTEM_PROMPT = prompt

def init_files(): #init any files to specific states when you start up phyz
    # as of 8/29 being used just to reset the state of speak_status.txt, transcribe_status.txt, and seen/spoken_to_mentors.txt to be blank on start
    with open("speak_status.txt", "w", encoding="utf-8") as f:
        f.write("")

    with open("transcribe_status.txt", "w", encoding="utf-8") as f:
        f.write("")

    with open("spoken_to_mentors.txt", "w", encoding="utf-8") as f:
        f.write("")

    with open("seen_mentors.txt", "w", encoding="utf-8") as f:
        f.write("")


def augment_prompt_with_mentors(base_prompt, mentor_file="seen_mentors.txt"):
    try:
        with open(mentor_file, "r", encoding="utf-8") as f:
            mentors = [line.strip() for line in f if line.strip()]
        if mentors:
            mentor_line = "You can also address any of the following names if you have a question: " + ", ".join(mentors) + "."
            return f"{base_prompt}\n{mentor_line}"
    except FileNotFoundError:
        pass
    return base_prompt


def audio_recorder_loop():
    with open("speak_status.txt", "r") as f:
        status = f.read().strip().lower()
        while True and status != "speaking":
            currentSerial = ''
            #ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # 14:30:22.123
            #print(f"[{ts}] BAHADIR - this is OUTSIDE the if statement")

            if serialObj is not None and listeningmode == False:
                serialObj.timeout = None  # blocking read
                raw = serialObj.read()
                currentSerial = raw.decode('ascii', errors='ignore') if raw else ''
                #print(currentSerial)
            if (listeningmode == True) or (currentSerial == '4'):
                frequency = random.randint(400, 1000) # Set Frequency
                duration = 300 # Set Duration To 1000 ms == 1 second
                


                if os.getenv("COMPUTERNAME") == "PHYZ":
                    import winsound
                    winsound.Beep(frequency, duration)
                    winsound.PlaySound('SystemAsterisk', winsound.SND_ALIAS)
                elif os.environ.get("COMPUTERNAME") == "AYAANMAC":
                    os.system('afplay /System/Library/Sounds/Glass.aiff')


                audio = record_until_silence(timeout=20)  # seconds
                audio_queue.put(audio)

                f.seek(0)
                status = f.read().strip().lower()

                while True and status == "speaking":
                    time.sleep(0.1)
                    f.seek(0)
                    status = f.read().strip().lower()
                #print("Bahadir Debug listening loop")




def play_wav(raw: bytes):
    with BytesIO(raw) as filelike:
        samplerate, data = wavfile.read(filelike)
    sd.play(data, samplerate)
    sd.wait()



def main():
    init_files()
    model = whisper.load_model("base")  # Load Whisper model once
    dad_jokes = DadJokes()  # Load jokes once
    apologies = Apologies()  # Load apologies once
    thinking_lines = ThinkingLines()
    memory_db = MemoryDB()  # Persistent memory storage (semantic vector store)

    #control_queue = remote_control.start_auto() #I don't know what this is for
    last_idle_response_time = 0  # separate from last user interaction
    IDLE_PROMPT_INTERVAL = 15    # seconds between idle prompts

    # Track most recent question/answer pair for "remember that" support
    last_user_query = None
    last_assistant_response = None

    global last_interaction_time

    print("PHYZAI is listening... Say 'exit' to quit.")


    #############################
    ###     Recorder Loop     ###
    #############################
    #TODO: Make button activated option
    #would add a if statement at the front like:
    #if button flag true then

    recorder_thread = threading.Thread(target=audio_recorder_loop, daemon=True)   # This is the thread that runs record until silence
    recorder_thread.start()

#for speak, need to add Bahadir digital out for mouth
#    serialObj.write(HIGH_COMMAND)
#    serialObj.flush()

#    around 
#    speak("text")

#    serialObj.write(LOW_COMMAND)   
#    serialObj.flush()



    while True:
        try:
            # Try to get recorded audio
            audio_bytes = audio_queue.get(timeout=1)  # wait max 1 sec
            #print("Bahadir Debug speaking loop")

        except queue.Empty:
            current_time = time.time()

            #check to see if there are any new mentors in screen
            if audio_queue.empty():  # or similar condition to ensure Phyz is not busy
                check_for_new_mentors_and_greet(speak)


            response, last_idle_response_time = check_idle_and_prompt_chatgpt(
                last_interaction_time, last_idle_response_time, memory_db
            )
            if response:
                print(f"PHYZAI (idle): {response}")
                speak(response)
            continue


        ########################################################
        #####                Transcription                ######
        ########################################################

        #TODO: make button activated option (would look like below comments)
        #if button activated true
        #   if button pressed set pressed flag true
        #       if button not pressed and pressed flag is true then call record until silence       
        #(This allows us to not accidentally double call a method if the button is being held down)

        voice_db = Voice_DB()
        speaker = voice_db.find_speaker(audio_bytes)

        transcription = transcribe_audio(model, audio_bytes)

        rp(f"[cyan][bold]{speaker} said:[/] {transcription}[/]")
        normalized = transcription.lower().strip().strip(".!?")

        #############################################################
        # Handle exit command
        #############################################################
        if normalized == "exit" or "fizz exit" in normalized:
            print("Goodbye! PHYZAI session ended.")
            speak("goodbye")
            break

        # Handle LLM switch voice commands
        if "fizz switch to gemini" in normalized:
            with open("llm2use.txt", "w", encoding="utf-8") as f:
                f.write("gemini")
            rp("[green]Switched LLM to Gemini[/]")
            continue
        if "fizz switch to claude" in normalized:
            with open("llm2use.txt", "w", encoding="utf-8") as f:
                f.write("claude")
            rp("[green]Switched LLM to Claude[/]")
            continue
        if "fizz switch to chatgpt" in normalized:
            with open("llm2use.txt", "w", encoding="utf-8") as f:
                f.write("chatgpt")
            rp("[green]Switched LLM to ChatGPT[/]")
            continue

        # New: flush queue via voice command
        if normalized in ("flush", "clear queue", "clear audio queue"):
            flush_audio_queue()
            rp("[yellow]Audio queue flushed[/]")
            continue

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

        # Say thinking line while PHYZ figures out what its saying and renders it (These have not been prefabed yet)
        if random.random() < 0.5:
            thinking = thinking_lines.get_random_think_line()
            if thinking:
                print(f"PHYZAI (thinking): {thinking.text}")
                play_wav(thinking.raw)

 
        # Otherwise normal GPT response
        trigger_words = [
            "phyz", "fizzy", "fizz", "phizz", "fizzay", "phiz", "phys", "fisy",
            "fizzey", "fizzzy", "phisy", "fiz", "fizzee", "phizzy",
            "thiz",
        ]

        normalized = transcription.lower()

        #Make prompt include mentors to address if Phyz is confused
        enhanced_prompt = augment_prompt_with_mentors(SYSTEM_PROMPT)

        # If user asked Phyz to remember the last Q/A pair, store it and don't call the LLM
        if "remember that" in normalized or "remember this" in normalized:
            if last_user_query and last_assistant_response:
                memory_text = f"Q: {last_user_query}\nA: {last_assistant_response}"
                memory_db.add_memory(memory_text)
                rp(f"PHYZAI: [bold bright_green]memorized[/] {memory_text}")
                speak("Got it. I will remember that.")
            else:
                rp("PHYZAI: [yellow]No previous question/answer to remember yet.[/]")
                speak("I don't have anything to remember yet.")
            continue

        with open("names2know.txt", "r") as nameFile: # Keep this updated please
            for name in nameFile.readlines():
                if f"I am {name.strip().lower()}" in normalized or f"This is {name.strip().lower()}" in normalized:
                    # TODO have a json file to keep track of who is seen and who isn't
                    with open("seen_mentors.txt", "a+", encoding="utf-8") as f:  # read and append mode
                        f.seek(0) #start at beginning of file
                        contents = f.read()
                        if name.strip().lower() not in contents:
                            f.write(f"{name.strip().lower()}\n")
                            if DEBUG.DEBUG_MODE: print(f"added {name.strip().lower()} to seen mentors file")

        #the speaker name has to be registered in names2know anyway, so we don't really need to check that here, its more for the database of users for vision
        #TODO possibly could check the last speaker, and compare them so you only change the spoken mentors file if the speaker changes
        if speaker.strip().lower() != "unknown user":
            with open("spoken_to_mentors.txt", "w", encoding="utf-8") as f:  # read/write mode
                    f.write(f"{speaker.strip().lower()}\n")
                    if DEBUG.DEBUG_MODE: print(f"added {speaker.strip().lower()} to seen spoken mentors file")


        # Respond with Chat if Phyz is mentioned
        if any(word in normalized for word in trigger_words):
            # bahadir addition - three lines below
            flush_audio_queue()
            with open("speak_status.txt", "w", encoding="utf-8") as f:
                f.write("speaking")
                #print("Bahadir Debug heard Phyz")

            # Add relevant memories to the prompt before calling the LLM
            memory_context = None
            memories = memory_db.query(transcription, top_k=5)
            if memories: #adds the speaker context to the memories as well
                memory_context = ""
                for m in memories:
                    try:
                        s = m["metadata"]["speaker"]
                        memory_context += (f"- {s} said {m['text']}")
                    except (KeyError, TypeError) as e:  # excepting in case the metadata doesn't exist or is None
                        memory_context += (f"- {m['text']}")
                    memory_context += "\n"

            llm_choice = "chatgpt"
            try:
                with open("llm2use.txt", "r", encoding="utf-8") as llm_file:
                    llm_choice = llm_file.read().strip().lower() or "chatgpt"
            except FileNotFoundError:
                pass

            if llm_choice == "gemini":
                response = ask_gemini(enhanced_prompt, transcription, memory_context=memory_context)
            elif llm_choice == "claude":
                response = ask_claude(enhanced_prompt, transcription, memory_context=memory_context)
            else:
                transcription_w_speaker = f"{speaker} said: {transcription}"
                response = ask_chatgpt(enhanced_prompt, transcription_w_speaker, memory_context=memory_context)

                with ThreadPoolExecutor() as executor:
                    future = executor.submit(should_remember, transcription_w_speaker, memory_db) #passes in memory and transcription
                    result = future.result()

                # result = should_remember(transcription, memory_db) # without the second thread, can toggle off & on for testing

                if result:
                    to_remember = f"A: {response}" #TODO FIXED -  I don't think we need to store the answer as apart of what we remember but we can for this example
                    if speaker != "Unknown User": metadata = {"speaker": speaker} #first try to assign speaker from the voice
                    else:
                        #then try from whoever is being seen
                        with open("seen_mentors.txt", "r", encoding="utf-8") as f:
                            metadata = ""
                            line = f.readlines()
                            if line is not None:
                                metadata = {"speaker": line}  # just throwing whoever is seen onto the speaker metadata

                    memory_db.add_memory(to_remember, metadata=metadata)


            if response:
                last_interaction_time = time.time()
                last_user_query = transcription
                last_assistant_response = response
                rp(f"PHYZAI: [bold bright_green]saying[/] [green]llm[/] {response}")
                speak(response)


        if (check_idle_and_prompt_chatgpt(last_interaction_time, last_idle_response_time, memory_db))[0]:
            last_interaction_time = time.time()


def flush_audio_queue(q: queue.Queue = audio_queue):
    """
    Drain all currently queued audio frames without blocking.
    Note: this is not atomic with producers — new items may be added
    while draining. For atomic swap, use a Lock and replace the queue.
    """
    try:
        while True:
            q.get_nowait()
    except queue.Empty:
        return


if __name__ == "__main__":
    main()