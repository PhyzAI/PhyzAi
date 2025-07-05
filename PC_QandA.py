## PhyzAI - A STEAM Chatbot                      ##
## Pete Curran - 2023 - curranpete@gmail.com       ##

import asyncio  # have multiple tasks running at once
import csv  # csv library
import datetime  # date and time library
import os  # Operating system library
import random  # random number generator
import re
import time
import winsound  # make beeping noises

import openai  # OpenAI API library
import pyttsx3  # pythons text to speech library
import serial
import speech_recognition as sr  # Speech recognition library
import whisper

import prompts  # The prompts for the chatbot

# Key for the openAI API - this is set as an environment variable: 
# https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety
openai.api_key = os.environ["OPENAI_API_KEY"]

# initialize text to speach
engine = pyttsx3.init()
engine.setProperty('rate', 200)
engine.setProperty('volume', 1)

whisperModel = whisper.load_model("tiny.en")

say_command = re.compile(r'^(?:hey )?(?:phyz|fizz|this),? say (.*)$', re.IGNORECASE)
please_command = re.compile(r'^(?:phyz|fizz|this),? please', re.IGNORECASE)

toSay = ''
recognised_speech = ''
slowTaskComplete = False
inSpeaking = False
stopped = False
beepTask = ''
timeWait = 15


time.sleep(1)

firstListen = True
firstExit = True
firstInnapropriate = True


# This function is the core of the chatbot. It sets the personality for the bot, and sends the question to openAI.
async def ask(question: str, DEBUG=False, OVERRIDE=False):
    global toSay
    global slowTaskComplete
    global stopped

    slowTaskComplete = False

    """Sends a question to the openAI API and returns the answer. Set OVERRIDE to True to override constraints on the answer."""
    # If the override is set, select the more general prompt.
    # print("in ask")

    if OVERRIDE:
        prompt = prompts.OVERRIDEPROMPT
    else:
        prompt = prompts.MAINPROMPT

    # Open a request to openai
    print("actually asking")
    frequency = random.randint(200, 1000)  # Set Frequency To 2500 Hertz
    duration = 100  # Set Duration To 1000 ms == 1 second
    winsound.Beep(frequency, duration)
    await asyncio.sleep(1)
    frequency = random.randint(200, 1000)  # Set Frequency To 2500 Hertz
    duration = 100  # Set Duration To 1000 ms == 1 second
    winsound.Beep(frequency, duration)
    #currentSerial = serialObj.read().decode('ascii')

    print("asking")
    print(currentSerial)
    question = question.lstrip()
    print(question)
    response = ''


    print("Asking ChatGPT")
    start_time = time.perf_counter()
    response = openai.ChatCompletion.create(
        # Select the model to answer the question
        model="gpt-4o",

        # Set the personality of the bot. The 'system' role tells the bot who it is.
        # The 'user' role is the question the user has asked.
        messages=[
            {"role": "system",
             "content": prompt},
            {"role": "user", "content": question}
        ]
    )

    end_time = time.perf_counter()
    print(f"Total request duration: {end_time - start_time} seconds")
    toSay = response['choices'][0]['message']['content']

    # If you set the DEBUG flag to True, it will print the whole response here.
    # This is useful for seeing how many tokens the response cost.
    if DEBUG:
        print(response)

    # await asyncio.sleep(10)
        print("got answer")
        slowTaskComplete = True
        # print("slow task complete")



async def askWithWait():
    print("in ask with wait")
    global slowTaskComplete
    global recognised_speech
    global beepTask
    global timeWait

    timeWait = 10
    startTime = time.time()
    attempt = 1
    slowTask = asyncio.create_task(ask(recognised_speech))
    while not slowTaskComplete:
        await asyncio.sleep(0)
        if slowTaskComplete:
            break
        elif (time.time() - startTime) >= timeWait:
            apologize()
            attempt = attempt + 1
            timeWait = timeWait + 10
        if attempt == 3:
            print("printing leaving")
            speak("Communication channels seem to be having issues. Let us try another question please.")
            slowTask.cancel()
            return
    try:
        await slowTask
        slowTaskComplete = False
    except asyncio.CancelledError:
        print("cancelled")



def controller():
    global firstListen
    global firstExit
    global firstInnapropriate
    global stopped

    input("Press Enter to continue...")
    print("saw button press")
    listen()
    speak(toSay)


# This function plays the output we get back from the API.
def speak(text: str) -> None:
    """Plays the text using python text to speech"""
    print("in speak")
    global inSpeaking
    inSpeaking = True

    # Select the voice to use and pass it the text to read.
    # get todays date
    today = datetime.date.today()

    now = datetime.datetime.now()
    timeString = now.strftime("%H:%M:%S")

    # check and make question directory
    if not os.path.exists("answers"):
        os.makedirs("answers")

    # append current question to the csv
    with open("answers/%s.csv" % today, "a", newline="", encoding='utf-8') as answers:
        # creating writer object
        csv_writer = csv.writer(answers)
        # appending data
        current_data = [today, timeString, text]
        csv_writer.writerow(current_data)


    engine.say(text)
    engine.runAndWait()
    engine.stop()

    inSpeaking = False
    return




# This is the main loop of the program. It listens for the user to say something, then sends it to the API.
def listen(OVERRIDE=False) -> None:
    """Listens for audio and calls other functions to fetch and play a response."""
    # Obtain audio from the microphone using the speech recognition library
    # Create a listener object
    print("in listen")

    r = sr.Recognizer()

    global toSay
    global recognised_speech

    # Start a loop to listen for audio
    # while keyboard.is_pressed('1'):

    # sr uses the default microphone to listen for audio. If there is more than one mic, you may have to set this.
    # https://pypi.org/project/SpeechRecognition/
    with sr.Microphone() as source:
        # for index, name in enumerate(sr.Microphone.list_microphone_names()):
        # print("Microphone 7with name \"{1}\" found for `Microphone(device_index={0})`".format(index, name))
        print("Listening!")  # You don't need this, but it's useful when debugging.
        frequency = random.randint(200, 1000)  # Set Frequency To 2500 Hertz
        duration = 1000  # Set Duration To 1000 ms == 1 second
        winsound.Beep(frequency, duration)
        print("Beep 1!")  # You don't need this, but it's useful when debugging.

        
        
        audio = r.listen(source, timeout=10)
        print("After listen!")  # You don't need this, but it's useful when debugging.


    # Recognise the speech using Whisper API
    try:
        # Send the audio from speech recognition to the Whisper API
        print("before whisper")
        with open('audioFile.wav', 'wb') as file:
            file.write(audio.get_wav_data())
            #   file.write(audio)

            # Bahadir comment   file.flush()
            file.close()
        assert os.path.exists("c:\\Users\\bahad\\OneDrive\\Documents\\GitHub\\PhyzAi\\audioFile.wav")
        from pathlib import Path
        my_path = Path('c:\\Users\\bahad\\OneDrive\\Documents\\GitHub\\PhyzAi\\audioFile.wav')
        transcribe_response = whisperModel.transcribe(str(my_path))
        recognised_speech = transcribe_response["text"]
        # recognised_speech = r.recognize_whisper_api(audio, api_key=os.environ['OPENAI_API_KEY'])
        print(
            f"Whisper API thinks you said {recognised_speech}")  # You don't need this, but it's useful when debugging.

        # get todays date
        today = datetime.date.today()

        now = datetime.datetime.now()
        timeString = now.strftime("%H:%M:%S")

        # check and make question directory
        if not os.path.exists("questions"):
            os.makedirs("questions")

        # append current question to the csv
        with open("questions/%s.csv" % today, "a", newline="", encoding='utf-8') as questions:
            # creating writer object
            csv_writer = csv.writer(questions)
            # appending data
            current_data = [today, timeString, recognised_speech]
            csv_writer.writerow(current_data)

        # Handle the response from the API. If OVERRIDE is set, use the more general prompt.
        # Speak takes the audio, calls the API, and plays the response.
        if OVERRIDE:
            asyncio.run(askWithWait())
        else:
            asyncio.run(askWithWait())
            # If the speech recognition library fails, this will throw on the computer.
    except sr.RequestError as e:
        print("Could not request results from Whisper API")


# Run listen when the program launches
# You'll want to update this when you add your button(s)
if __name__ == "__main__":

    print("Welcome to Phyz AI, press 4 to ask a question or 3 to stop the question and 5 to leave")
    # Bahadir debug
    print("Bahadir 20250322")

    while True:
        controller()
