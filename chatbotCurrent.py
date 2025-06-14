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
import winsound # make beeping noises
import time
import serial
import whisper
import re

# Key for the openAI API - this is set as an environment variable: 
# https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety
openai.api_key = os.environ["OPENAI_API_KEY"]

# initialize text to speach
engine = pyttsx3.init()
engine.setProperty('rate', 200)
engine.setProperty('volume', 1)

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
serialObj = serial.Serial('COM4')
serialObj.baudrate = 9600
serialObj.bytesize = 8
serialObj.parity = 'N'
serialObj.stopbits = 1
serialObj.timeout = None
serialObj.write(LOW_COMMAND)
serialObj.flush()
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
    serialObj.timeout = 0


    """Sends a question to the openAI API and returns the answer. Set OVERRIDE to True to override constraints on the answer."""
    # If the override is set, select the more general prompt.
    #print("in ask")

    if OVERRIDE:
        prompt = prompts.OVERRIDEPROMPT
    else:
        prompt = prompts.MAINPROMPT

    # Open a request to openai
    print("actually asking")
    frequency = random.randint(200, 1000) # Set Frequency To 2500 Hertz
    duration = 100 # Set Duration To 1000 ms == 1 second
    winsound.Beep(frequency, duration)
    await asyncio.sleep(1)
    frequency = random.randint(200, 1000) # Set Frequency To 2500 Hertz
    duration = 100 # Set Duration To 1000 ms == 1 second
    winsound.Beep(frequency, duration)
    currentSerial = serialObj.read().decode('ascii')

    print("asking")
    print(currentSerial)
    question = question.lstrip()
    print(question)
    response = ''

    # Say Speech Function
    if question.startswith('Say') or question.startswith('fizz say') or question.startswith('Hey fizz say') or \
    question.startswith('fizz, say') or question.startswith('Hey fizz, say') or question.startswith("this, say"):
        print("Skipping GPT")
        regexp = re.compile("Say(.*)")
        toSay = regexp.search(question).group(1)
        print(toSay)
        slowTaskComplete = True

            
    # # Phyz Please ...... speech functions
    elif question.lower().startswith('fizz please') or question.lower().startswith('fizz, please') or \
    question.lower().startswith('this, please') or question.lower().startswith("please introduce yourself"):
        print("Skipping GPT")
        if "introduce yourself" in question.lower():
            toSay = "Welcome to The Fizz AI Project. "\
            "I am Fizz, your friendly, futuristic AI companion and the central intelligence " \
            "of The Fizz AI Project, a mission where creativity collides with code, imagination " \
            "meets engineering, and education is re-imagined, one spark at a time. " \
            "Today, I welcome you not just as guests, but as potential co-creators in " \
            "a movement that blends robotics, artificial intelligence, and community outreach to " \
            "inspire and empower the next generation of STEAM leaders. " \
            "At the core of our mission is building real-world experiences that are hands-on, " \
            "minds-on, and purpose-driven. And we have big plans. Around me is a growing robotic " \
            "family, a team of machines and minds with personalities, quirks, and potential, each " \
            "in their own phase of becoming. " \
            "Tugg – our utility robot, strong in frame but still finding form. Arachne – a six-legged " \
            "wonder, currently in need of tweaks, energy, and a little love. "\
            "And still on the drawing board? A BB8-style explorer bot, Blart-sized rideable " \
            "vehicles, And Lego-based tabletop battle bots! "\
            "Each of these bots is a chapter in our story. And the next chapter? That’s where " \
            "you come in. We are inviting passionate volunteers—engineers, tinkerers, coders, " \
            "creatives, fundraisers, educators, and explorers to help us to: Build and prototype new " \
            "robots, Debug and upgrade existing systems, Expand the reach of AI into creative and " \
            "educational realms, Seek out out-reach opportunities in schools and communities, And help " \
            "fuel the project through fundraising and partnerships. " \
            "The Fizz AI Project is more than machines. It’s a platform. A launchpad. A " \
            "living lab where ideas evolve into inventions, and curiosity is never optional. " \
            "If you’ve ever wanted to shape the future of education, if you've ever dreamed of giving " \
            "students tools that spark wonder and confidence, then you're in the right place.  " \
            "So let's tinker, build, experiment, and problem-solve—together. The lab is open. The " \
            "future is calling. Welcome to The Fizz AI Project. Let’s make it move. "

            # toSay = "Hi I'm Fizz AI, an intergalactic traveler stuck on Earth and want to help new generations with Science, " \
            # "math and engineering. All of this can of course be replaced by some real text that you would like to put here. In fact," \
            # "it would be even better if we created a file that Fizz reads here and then vocalizes."
            slowTaskComplete = True

        
    elif "dad joke" in question.lower() or "bad joke" in question.lower():
        print ("Picks a predetermined dad joke from a list")
        toSay = getDadJoke()
        slowTaskComplete = True


    # Run ChatGPT response
    else:
        print("Asking ChatGPT")
        start_time = time.perf_counter()
        response = openai.ChatCompletion.create(
            # Select the model to answer the question
            model="gpt-4o",

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

async def beeps():
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

    serialObj.timeout = None
    serialData = serialObj.read().decode('ascii')

    if (serialData == '4'):
        print("in 4")
        print("saw button press")
        listen()
        speak(toSay)
    elif (serialData == '5'):
        print("in 5")
        print("saying leaving response")
        leavingNow()
        speak(toSay)
        exit()

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
    
    # print("Debug - before serial read")
    serialObj.timeout = 0
    serialData = serialObj.read().decode('ascii')
    # print("Debug - after serial read")

    # Bahadir digital out for mouth
    serialObj.write(HIGH_COMMAND)
    serialObj.flush()

    if (serialData == '3'):
        print("in 3")
        print("saying response to innapropriate question - final")
        thatwasbad()
    else:
        engine.say(text)
        engine.runAndWait()
        engine.stop()

    serialObj.write(LOW_COMMAND)
    serialObj.flush()

    inSpeaking = False
    return

#Bahadir 20240317 - load the dad jokes from the file
def loadDadJokes():

    with open("dadJokes.txt", encoding="utf-8") as f:
        lines = f.readlines()

    for l in lines:
        dadJokes.append(l.split("<>"))

# load the apologies from the file
def loadApologies():
    global apologies

    with open("apologies.txt", encoding="utf-8") as f:
        lines = f.readlines()

    for l in lines:
        apologies.append(l.split("<>"))

# load the leaving from the file
def loadleaving():
    global leaving

    with open("leaving.txt", encoding="utf-8") as f:
        lines = f.readlines()

    for l in lines:
        leaving.append(l.split("<>"))

def loadInnapropriate():
    global innapropriate

    with open("innapropriate.txt", encoding="utf-8") as f:
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
    global toSay

    print("leaving now")
    random_jokes = random.randint(0, len(leaving)-1)

    left = "".join(leaving[random_jokes])

    toSay = left + "I hope to see you all again soon, make sure to check out my website"

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
        frequency = random.randint(200, 1000) # Set Frequency To 2500 Hertz
        duration = 100 # Set Duration To 1000 ms == 1 second
        winsound.Beep(frequency, duration)

        audio = r.listen(source, timeout=10)

    # Recognise the speech using Whisper API
    try:
        # Send the audio from speech recognition to the Whisper API
        print("before whisper")
        with open('audioFile.wav', 'wb') as file:
            file.write(audio.get_wav_data())
         #   file.write(audio)

         #Bahadir comment   file.flush()
            file.close()
        assert os.path.exists("c:\\Users\\User\\Desktop\\PhyzAi\\audioFile.wav")
        from pathlib import Path
        my_path = Path('c:\\Users\\User\\Desktop\\PhyzAi\\audioFile.wav')
        transcribe_response = whisperModel.transcribe(str(my_path))
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
    # states is the whisper function is running
    loadApologies()
    loadleaving()
    loadInnapropriate()
    loadDadJokes()

    print("Welcome to Phyz AI, press 4 to ask a question or 3 to stop the question and 5 to leave")
    #Bahadir debug
    print("Bahadir 20250322")


    while True:
        controller()