# Hi, I'm PhyzAI!

This code creates an audio interface for the PhyzAI chatbot.
It's designed to be implemented with a button press.

# It runs on three main libraries:

## WhisperAI (through speechrecorder)
WhisperAI listens until the user says something, then uses an API to interpret the audio.

## OpenAI
OpenAI takes the output from WhisperAI, and comes up with a suitable response. It's limited by its prompt.

## Google tts
Google Text To Speech (gTTS) takes the output from OpenAI and says it out loud.
Note that gTTS can only play saved audio, so the audio is saved to the audio folder, played, then deleted.

# Bits that cost money
Using OpenAI and WhisperAI cost tokens via your OpenAI API key. 4000 characters is about 1000 tokens, which costs $0.002.

# The OpenAI key
The OpenAI API key is set as an environment variable. You can set these through the windows control panel.