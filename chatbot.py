## PhyzAI - A STEAM Chatbot                      ##
## Pete Curran - 2023 - curranpete@gmail.com       ##

import openai # OpenAI API library
import os # Operating system library
from gtts import gTTS # Google text to speech library
import pyttsx3 #pythons text to speech library
import playsound # Library to play Google text to speech
import speech_recognition as sr # Speech recognition library
import prompts # The prompts for the chatbot
import datetime # date and time library
import csv # csv library
import keyboard # get key presses
import random # random number generator
import multiprocess
import threading
import time

# Key for the openAI API - this is set as an environment variable: 
# https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety
openai.api_key = os.environ["OPENAI_API_KEY"]

# initialize text to speach
engine = pyttsx3.init()

# init dad jokes
jokes = []

toSay = ''

# This function is the core of the chatbot. It sets the personality for the bot, and sends the question to openAI.
def ask(question: str, DEBUG=False, OVERRIDE=False) -> str:
    """Sends a question to the openAI API and returns the answer. Set OVERRIDE to True to override constraints on the answer."""
    # If the override is set, select the more general prompt.
    if OVERRIDE:
        prompt = prompts.OVERRIDEPROMPT
    else:
        prompt = prompts.MAINPROMPT

    # Open a request to openai
    response = openai.ChatCompletion.create(
        
        # Select the model to answer the question. 3.5 is cheap and fast. 
        # 4 would offer better answers, but is much more expensive.
        model="gpt-3.5-turbo",

        # Set the personality of the bot. The 'system' role tells the bot who it is.
        # The 'user' role is the question the user has asked.
        messages=[
            {"role":"system",
                "content":prompt},
            {"role":"user","content":question}
        ]
    )

    # If you set the DEBUG flag to True, it will print the whole response here.
    # This is useful for seeing how many tokens the response cost.
    if DEBUG:
        print(response)

    return response['choices'][0]['message']['content']

# This function plays the output we get back from the API.
def speak(text: str) -> None:
    """Plays the text using python text to speech"""

    # Select the voice to use and pass it the text to read.
    # get todays date
    today = datetime.date.today()

    now = datetime.datetime.now()
    timeString = now.strftime("%H:%M:%S")

    # check and make question directory
    if not os.path.exists("answers"):
        os.makedirs("answers")

    # check and make todays csv
    if not os.path.exists("answers\%s.csv" % (today)):
        open("%s.csv" % (today), 'a').close()

    # append current question to the csv
    with open("answers\%s.csv" % (today),"a",newline="") as answers:
        # creating writer object
        csv_writer=csv.writer(answers)
        # appending data
        current_data = [today, timeString, text]
        csv_writer.writerow(current_data)
    
    engine.say(text)
    engine.runAndWait()
    engine.stop()

    return

# load the dad jokes from the file
def loadDadJokes():
    global jokes

    with open("dadjokes.txt", encoding="utf-8") as f:
        lines = f.readlines()

    for l in lines:
        jokes.append(l.split("<>"))

# say a random dad joke
def sayJoke():
    global jokes

    print("saying joke")
    random_jokes = random.randint(0, len(jokes)-1)

    joke = "".join(jokes[random_jokes])

    speak(joke)

# make sure that it hasn't been quiet for too long
def downTime():
    start = time.time()
    print("in downtime")
    while True:
        timeElapsed = time.time() -  start
        print(timeElapsed)
        if((timeElapsed) >= 1.0):
            sayJoke()
            print("said joke")
            break

# This is the main loop of the program. It listens for the user to say something, then sends it to the API.

def listen(OVERRIDE=False) -> None:
    """Listens for audio and calls other functions to fetch and play a response."""
    # Obtain audio from the microphone using the speech recognition library
    # Create a listener object
    r = sr.Recognizer()

    global toSay

    # Start a loop to listen for audio
    listening = True
    while keyboard.is_pressed('1'):

        # sr uses the default microphone to listen for audio. If there is more than one mic, you may have to set this.
        # https://pypi.org/project/SpeechRecognition/
        with sr.Microphone() as source:
            # for index, name in enumerate(sr.Microphone.list_microphone_names()):
                # print("Microphone with name \"{1}\" found for `Microphone(device_index={0})`".format(index, name))
            print("Listening!") # You don't need this, but it's useful when debugging.
            audio = r.listen(source)

        # Recognise the speech using Whisper API
        try:
            # Send the audio from speech recognition to the Whisper API
            recognised_speech = r.recognize_whisper_api(audio, api_key=os.environ['OPENAI_API_KEY'])
            print(f"Whisper API thinks you said {recognised_speech}") # You don't need this, but it's useful when debugging.

            # get todays date
            today = datetime.date.today()

            now = datetime.datetime.now()
            timeString = now.strftime("%H:%M:%S")

            # check and make question directory
            if not os.path.exists("questions"):
                os.makedirs("questions")

            # check and make todays csv
            if not os.path.exists("questions\%s.csv" % (today)):
                open("%s.csv" % (today), 'a').close()

            # append current question to the csv
            with open("questions\%s.csv" % (today),"a",newline="") as questions:
                # creating writer object
                csv_writer=csv.writer(questions)
                # appending data
                current_data = [today, timeString, recognised_speech]
                csv_writer.writerow(current_data)
            # Handle the response from the API. If OVERRIDE is set, use the more general prompt.
            # Speak takes the audio, calls the API, and plays the response.
            if OVERRIDE:
                toSay = ask(recognised_speech, OVERRIDE=True)
            else: 
                toSay = ask(recognised_speech)
            
            # If the speech recognition library fails, this will throw on the computer.
        except sr.RequestError as e:
            print("Could not request results from Whisper API")


# Run listen when the program launches
# You'll want to update this when you add your button(s)
if __name__ == "__main__":
    # states is the whisper function is running
    loadDadJokes()
    queue = multiprocess.Queue()
    while True:
        print("press 1 to talk to phyz")
        key = keyboard.read_key()
        if key == '1':
            listen()

            speak(toSay)
            
        if key == '2':
            exit()
            
import serial

# Configure the serial port
# arduino_port = '/dev/ttyACM0'  # Replace with the appropriate port name
# baud_rate = 9600  # Must match the baud rate set in Arduino code

# # Create a serial object
# ser = serial.Serial(arduino_port, baud_rate, timeout=1)

# Read data from Arduino
# while True:
    # try:
    #     # Read a line of data from Arduino
    #     data = ser.readline().decode().strip()
        
    #     # Print the received data
    #     print("Received data:", data)
        
    #     # Do something with the data
        
    # except KeyboardInterrupt:
    #     print("Monitoring stopped by the user.")
    #     break

# # Close the serial connection
# ser.close()