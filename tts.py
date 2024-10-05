import pyttsx3

class _TTS:

    engine = None
    rate = None
    def __init__(self):
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('rate', 187) # was 187
        self.engine.setProperty('volume', 1)
        #self.engine.setProperty('voice', voices[0].id) # voices[0] male, voices[1] female
        #self.engine.setProperty('pitch', 2.0) # 1.0 default
        

    def start(self,text_):
        self.engine.say(text_)
        self.engine.runAndWait()