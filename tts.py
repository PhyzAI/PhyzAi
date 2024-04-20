import pyttsx3

class _TTS:

    engine = None
    rate = None
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 200)
        self.engine.setProperty('volume', 1)


    def start(self,text_):
        self.engine.say(text_)
        self.engine.runAndWait()