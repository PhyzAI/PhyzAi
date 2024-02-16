import keyboard
import time

from listener import Listener
from stt import Speech2TextModel
import pyttsx3
import speech_recognition as sr
import os

import multiprocess
from functools import partial

from threading import Thread

talker = pyttsx3.init()

def playSound(queue: multiprocess.Queue):

    while True:
        if queue.empty():
            talker.say("thinking")
            talker.runAndWait()
        else:
            talker.say(queue.get())
            talker.runAndWait()
            break

def chatbotRespond(text: str, queue: multiprocess.Queue):
    from chatgpt import Chat
    chatbot = Chat()
    response = chatbot.respond(text)
    queue.put(response)

def main():
    listener = sr.Recognizer()

    print("whisper model loaded")
    queue = multiprocess.Queue()

    while True:
        try:
            if keyboard.is_pressed('1'):
                with sr.Microphone() as source:
                    print("listening")
                    audio = listener.listen(source)
            
                if audio:
                    text = listener.recognize_whisper_api(audio, api_key=os.environ['OPENAI_API_KEY'])
                    print(f"Whisper API thinks you said {text}") # You don't need this, but it's useful when debugging.

                    # spawn two processes - on playsound process, it will keep playing "thinking" 
                    # while getting response from the chatbotRespond process 
                    func1 = partial(chatbotRespond, text)
                    process1 = Thread(target=func1, args=(queue, ))
                    process2 = Thread(target=playSound, args=(queue, ))

                    process2.start()
                    process1.start()

                    process2.join()
                    process1.join()

        except KeyboardInterrupt:
            break

        time.sleep(0.25)

if __name__ == "__main__":
    main()