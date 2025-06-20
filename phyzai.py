import sounddevice as sd
import whisper
from scipy.io import wavfile

from apologies import Apologies
from dadjokes import DadJokes
from transcribe2gpt import ask_chatgpt
from transcriber import record_until_silence, transcribe_audio
from tts import speak

SYSTEM_PROMPT = (
    "You are now phyzai. You are an educational robot designed for kids listening to their speech. "
    "Try to answer everything in a fun and interactive way best designed to fully explain their STEM related questions."
    "It is important to be concise and not too verbose, but also not too short."
    "make sure to be funny as well! Please keep all answers to 1-2 scentences"
)


def play_wav(path: str):
    samplerate, data = wavfile.read(path)
    sd.play(data, samplerate)
    sd.wait()


def main():
    model = whisper.load_model("base")  # Load Whisper model once
    dad_jokes = DadJokes()  # Load jokes once
    apologies = Apologies()  # Load apologies once

    print("PHYZAI is listening... Say 'exit' to quit.")

    while True:
        audio_bytes = record_until_silence()
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
            print(f"PHYZAI: {joke}")
            play_wav(joke)
            continue
        elif dad_jokes.is_joke_request(normalized) and normalized not in ["tell another", "another"]:
            joke = dad_jokes.get_random_joke()
            print(f"PHYZAI: {joke}")
            play_wav(joke)
            continue
        else:
            # Reset joke flag only if input is NOT joke related
            dad_jokes.reset_joke_flag()

        #############################################################
        # Check for apology requests
        #############################################################
        apology_response = apologies.handle_apology_request(transcription)
        if apology_response:
            print(f"PHYZAI: {apology_response}")
            play_wav(apology_response)
            continue

        # Otherwise normal GPT response
        response = ask_chatgpt(SYSTEM_PROMPT, transcription)
        speak(response)
        print(f"PHYZAI: {response}")


if __name__ == "__main__":
    main()
