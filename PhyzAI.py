## PhyzAI - A STEAM Chatbot                      ##
## Pete Curran - 2023 - curranpete@gmail.com       ##

import openai # OpenAI API library
import os # Operating system library
import pyttsx3 #pythons text to speech library
import speech_recognition as sr # Speech recognition library
import prompts # The prompts for the chatbot
import datetime # date and time library
import csv # csv library
import keyboard # get key presses
import random # random number generator
import asyncio # have multiple tasks running at once
import threading
import winsound # make beeping noises
import time
import serial
import whisper
import re
import threading
from pathlib import Path
from tts import _TTS

# Presentation Helpers
from presentationConfig import PresentationConfig 
from slideshow import SlideShow

# Get current path of this file
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

# Key for the openAI API - this is set as an environment variable: 
# https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety
openai.api_key = os.environ["OPENAI_API_KEY"]

whisperModel = whisper.load_model("tiny.en")

# init apologies
apologies = []

dadJokes = []

# init mechanical errors
leaving = []

# init innapropriate responses
innapropriate = []

toSay = ''
recognised_speech = ''
slowTaskComplete = False
inSpeaking = False
stopped = False
beepTask = ''
timeWait = 15

# init communicatio with arduino
LOW_COMMAND = bytes('l', "utf-8")
HIGH_COMMAND = bytes('h', "utf-8")
try:    
    serialObj = serial.Serial('COM4')
    serialObj.baudrate = 9600
    serialObj.bytesize = 8
    serialObj.parity = 'N'
    serialObj.stopbits = 1
    serialObj.timeout = None
    serialObj.write(LOW_COMMAND)
    serialObj.flush()
except:
    print("Could not find anything on COM4")
    serialObj = None
time.sleep(1)

firstListen = True
firstExit = True
firstInnapropriate = True

# All the Threads
background_tasks = set()

# Conditions for multithreading
isListening = False
killSwitchOn = False
handlingButtons = True
SpeechRoutineThread = None
inSpeechRoutine = False

# Presentation mode state variables
inPresentationMode = False
currentSlide = 0
slideshowToPlay = "journals" # Set me to hardcode slideshow (uses the slideshow name from presentationconfig.xml)
pConfig = PresentationConfig("presentationconfig.xml")
currentSlideshow = SlideShow(pConfig.slideShows[slideshowToPlay])



def playSlideshow():
    global currentSlide
    global currentSlideshow

    print("Playing slide %i in the slideshow" % currentSlide)

    if currentSlide < len(currentSlideshow.slides):
        speak(currentSlideshow.slides[currentSlide].notes)

    currentSlide = currentSlide + 1


# This function is the core of the chatbot. It sets the personality for the bot, and sends the question to openAI.
def ask(question: str, DEBUG=False, OVERRIDE=False):
    global toSay
    global slowTaskComplete

    slowTaskComplete = False
    serialObj.timeout = 0


    """Sends a question to the openAI API and returns the answer. Set OVERRIDE to True to override constraints on the answer."""
    # If the override is set, select the more general prompt.
    #print("in ask")

    if OVERRIDE:
        prompt = prompts.OVERRIDEPROMPT
    else:
        prompt = prompts.MAINPROMPT

    #print("before AI")
    # Open a request to openai
    print("actually asking")
    frequency = random.randint(200, 1000) # Set Frequency To 2500 Hertz
    duration = 100 # Set Duration To 1000 ms == 1 second
    winsound.Beep(frequency, duration)
    # await asyncio.sleep(1)
    frequency = random.randint(200, 1000) # Set Frequency To 2500 Hertz
    duration = 100 # Set Duration To 1000 ms == 1 second
    winsound.Beep(frequency, duration)
    currentSerial = serialObj.read().decode('ascii')
    #if (serialObj.read().decode('ascii') == '3'):
    
    print("asking")
    print(currentSerial)
    question = question.lstrip()
    print(question)
    response = ''

    # Say Speech Function
    if question.startswith('Say'):
        print("Skipping gpt")
        regexp = re.compile("Say(.*)")
        toSay = regexp.search(question).group(1)
        print(toSay)
        
    # # Phyz Please ...... speech functions
    elif question.lower().startswith('fizz please') or question.lower().startswith('fizz, please') or question.lower().startswith('this, please'):
        print("Skipping GPT")
        # speechPrompt =  re.compile("Fizz please(.*)").search(question).group(1)
        if "introduce yourself" in question.lower():
            toSay = "Hi I'm Fizz AI, I really really loooovvvee Bahadir mwah XOXO"
    
    elif "dad joke" in question.lower() or "bad joke" in question.lower():
        print ("Picks a predetermined dad joke from a list")
        toSay = getDadJoke()

    # Run ChatGPT response
    else:
        print("Asking ChatGPT")
        start_time = time.perf_counter()
        response = openai.ChatCompletion.create(
            # Select the model to answer the question. 3.5 is cheap and fast. 
            # 4 would offer better answers, but is much more expensive.
            model="gpt-3.5-turbo",

            # Set the personality of the bot. The 'system' role tells the bot who it is.
            # The 'user' role is the question the user has asked.
            messages= [
                {"role":"system",
                    "content":prompt},
                {"role":"user","content":question}
            ]
        )
        
        end_time = time.perf_counter()
        print(f"Total request duration: {end_time-start_time} seconds")
        toSay = response['choices'][0]['message']['content']


        # If you set the DEBUG flag to True, it will print the whole response here.
        # This is useful for seeing how many tokens the response cost.
        if DEBUG:
            print(response)

        #await asyncio.sleep(10)
        print("got answer")
        slowTaskComplete = True
        #print("slow task complete")

        # Speak fax
        speak(toSay)

"""
def beeps():
    global slowTaskComplete
    print("in beeps")
    
    frequency = random.randint(400, 800) # Set Frequency To 2500 Hertz
    duration = random.randint(10, 1000) # Set Duration To 1000 ms == 1 second
    winsound.Beep(frequency, duration)

    while True:
        print("in loop beeps before sleep")
        print("in loop beeps")
        frequency = random.randint(400, 800) # Set Frequency To 2500 Hertz
        duration = random.randint(10, 1000) # Set Duration To 1000 ms == 1 second
        winsound.Beep(frequency, duration)
        #controller()

        #await(SlowTask)
        #await asyncio.sleep(timeWait)
"""
"""
def askWithWait():
    print("in ask with wait")
    global slowTaskComplete
    global recognised_speech
    global beepTask
    global timeWait

    timeWait = 15
    startTime = time.time()
    attempt = 1
    slowTask = asyncio.create_task(ask(recognised_speech))
    while not slowTaskComplete:
        await asyncio.sleep(0)
        #print(time.time() - startTime)
        #print(slowTaskComplete)
        if slowTaskComplete:
            break
        elif (time.time() - startTime) >= timeWait:
            apologize()
            attempt = attempt + 1
            timeWait = timeWait + 30
        if attempt == 6:
            print("printing leaving")
            leavingNow()
    try:
        await slowTask
        slowTaskComplete = False
    except asyncio.CancelledError:
        print("cancelled")
"""
"""
def controller():
    global firstListen
    global firstExit
    global firstInnapropriate

    serialObj.timeout = None
    serialData = serialObj.read().decode('ascii')

    #if (serialObj.inWaiting() > 0):
    #print(serialObj.read().decode('ascii'))
    if (serialData == '4'):
        print("in 4")
        print("saw button press")
        listen()

    #Bahadir 20240317 - stop answering if 3 is pressed
    if(False):
        pass
    elif (serialData == '3'):
        print("in 3")
        print("saying response to innapropriate question")
        thatwasbad()
    elif (serialData == '5'):
        print("in 5")
        print("saying leaving response")
        leavingNow()
    elif (serialData == '3'):
        if(firstInnapropriate == False):  
            print("in 3")
            print("saying response to innapropriate question")
            thatwasbad()
        else:
            firstInnapropriate = False
    else:
        speak(toSay)
"""

# This function plays the output we get back from the API.
def speak(text: str) -> None:
    """Plays the text using python text to speech"""
    print("in speak")
    global inSpeaking
    global inSpeechRoutine
    inSpeaking = True

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
    # time.sleep(0)
    # Bahadir digital out for mouth
    serialObj.write(HIGH_COMMAND)
    serialObj.flush()

    engine = _TTS()
    engine.start(text)
    del(engine)

    serialObj.write(LOW_COMMAND)
    serialObj.flush()
    # Bahadir digital out for mouth
    # serialObj.digitalWrite(8, LOW)

    inSpeaking = False
    inSpeechRoutine = False
    print("Done speaking")
    return

#Bahadir 20240317 - load the dad jokes from the file
def loadDadJokes():

    with open("./config/dadJokes.txt", encoding="utf-8") as f:
        lines = f.readlines()

    for l in lines:
        dadJokes.append(l.split("<>"))

# load the apologies from the file
def loadApologies():
    global apologies

    with open("./config/apologies.txt", encoding="utf-8") as f:
        lines = f.readlines()

    for l in lines:
        apologies.append(l.split("<>"))

# load the leaving from the file
def loadleaving():
    global leaving

    with open("./config/leaving.txt", encoding="utf-8") as f:
        lines = f.readlines()

    for l in lines:
        leaving.append(l.split("<>"))

def loadInnapropriate():
    global innapropriate

    with open("./config/innapropriate.txt", encoding="utf-8") as f:
        lines = f.readlines()

    for l in lines:
        innapropriate.append(l.split("<>"))

# say a random apology
def apologize():
    global apologies

    #print("apologizing")
    random_jokes = random.randint(0, len(apologies)-1)

    apology = "".join(apologies[random_jokes])

    speak(apology)
    #print(joke)

# say a random comment about innapropriateness
def thatwasbad():
    global innapropriate

    print("innapropriate")
    random_innapropriate = random.randint(0, len(innapropriate)-1)

    dontaskthat = "".join(innapropriate[random_innapropriate])

    speak(dontaskthat)
    #print(joke)

# say leaving joke
def leavingNow():
    global leaving

    print("leaving now")
    random_jokes = random.randint(0, len(leaving)-1)

    left = "".join(leaving[random_jokes])

    speak(left)
    speak("I hope to see you all again soon, make sure to come check out my website and follow me on social media!")
    #print(joke)

#Bahadir 20240317 - tell a dad joke
def getDadJoke():

    print("Dad joke!")
    random_dadJoke = random.randint(0, len(dadJokes)-1)

    oneDadJoke = "".join(dadJokes[random_dadJoke])

    return oneDadJoke
    # speak(oneDadJoke)
    # print(oneDadJoke)

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
    #while keyboard.is_pressed('1'):

    # sr uses the default microphone to listen for audio. If there is more than one mic, you may have to set this.
    # https://pypi.org/project/SpeechRecognition/
    with sr.Microphone() as source:
        # for index, name in enumerate(sr.Microphone.list_microphone_names()):
            # print("Microphone 7with name \"{1}\" found for `Microphone(device_index={0})`".format(index, name))
        print("Listening!") # You don't need this, but it's useful when debugging.
        audio = r.listen(source, timeout=10, phrase_time_limit=2)
    print("done listening")
    # Recognise the speech using Whisper API
    try:
        # Send the audio from speech recognition to the Whisper API
        print("before whisper")
        with open('audioFile.wav', 'wb') as file:
            file.write(audio.get_wav_data())
         #   file.write(audio)

         #Bahadir comment   file.flush()
            file.close()

        audioFilePath = Path("{}\\audioFile.wav".format(BASE_DIR).replace("/","\\"))
        assert os.path.exists(audioFilePath)
        print(str(audioFilePath))

        transcribe_response = whisperModel.transcribe(str(audioFilePath))
        recognised_speech = transcribe_response["text"]
        # recognised_speech = r.recognize_whisper_api(audio, api_key=os.environ['OPENAI_API_KEY'])
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

        # no longer listening
        isListening = False
        
        # Speak takes the audio, calls the API, and plays the response.
        if OVERRIDE:
            ask(recognised_speech)
        else: 
            ask(recognised_speech)
        # If the speech recognition library fails, this will throw on the computer.
    except sr.RequestError as e:
        print("Could not request results from Whisper API")

        # no longer listening
        isListening = False
    

# Function to handle the button reading loop
def buttonHandler():
    global SpeechRoutineThread
    global inSpeechRoutine
    global currentSlide
    # SpeechRoutineThread = threading.Thread(target=listen)

    while handlingButtons:
        
        # For testing on other computers
        # serialData = str(input("Enter a command to simulate serial input [3,6]"))

        serialObj.timeout = None
        serialData = serialObj.read().decode('ascii')
        print("Recieved %i" % int(serialData))

        """
        3 = NC
        4 = Listen for user input
        5 = NC
        6 = Kill Switch
        """

        match serialData:
            case '3':
                playSlideshow()
                pass
            case '4':
                # Check to make sure we don't override a currently running speech routine thread
                if (not inSpeechRoutine):
                    # Make new speech routine thread and start it
                    SpeechRoutineThread = threading.Thread(target=listen)
                    SpeechRoutineThread.start()
                else:
                    print("Can't start a new speech routine, we are already in one qwq")

                isListening = True
                inSpeechRoutine = True
                pass
            case '6':
                
                pass
            case '5':
                killSwitchOn = True

                if currentSlide > 0:
                    currentSlide = currentSlide - 1
                    print("Moved to slide %i" % currentSlide)
                # SpeechRoutineThread.join()
                # # SpeechRoutineThread= None
                # print("Speech Routine Killed")
                # inSpeechRoutine= False
                pass
        


# Run listen when the program launches
# You'll want to update this when you add your button(s)
if __name__ == "__main__":
    # states is the whisper function is running
    loadApologies()
    loadleaving()
    loadInnapropriate()
    loadDadJokes()
    #try:
    print("Welcome to Phyz AI, press 4 to ask a question or 5 to stop the question and 3 to leave")

    # Startup Threading
    buttonHandlerThread = threading.Thread(target=buttonHandler)
    buttonHandlerThread.start()
    
    
    # while True:
    #     controller()