import random
import pyttsx3
    
class SpeechSynthesis:
    def __init__(self) -> None:
        self._engine = pyttsx3.init()
        self._jokes = []

    def setProperty(self, key: str, value):
        self._engine.setProperty(key, value)

    def loadDadJokes(self):
        with open("dadjokes.txt", encoding="utf-8") as f:
            lines = f.readlines()

        for l in lines:
            self._jokes.append(l.split("<>"))

    def say(self, text):
        self._engine.say(text)
        self._engine.runAndWait()

    # this function may not be useful 
    def sayJokes(self):
        print("telling you a dad joke")
        random_jokes = random.randint(0, len(self._jokes)-1)

        joke = "".join(self._jokes[random_jokes])

        self.say(joke)