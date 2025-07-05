import requests
from bs4 import BeautifulSoup
import os
import win32com.client


def text_to_speech(text, voice_index=2, rate=0, volume=100):
    """
    Convert text to speech using Windows SAPI (offline)
    
    Args:
        text (str): Text to convert to speech
        voice_index (int): Index of the voice to use (default: 0)
        rate (int): Speech rate (-10 to 10, default: 0)
        volume (int): Volume level (0 to 100, default: 100)
    """
    try:
        # Initialize the SAPI speaker
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        
        # Get available voices
        voices = speaker.GetVoices()
        
        # Set voice
        if 0 <= voice_index < voices.Count:
            speaker.Voice = voices.Item(voice_index)
            print(f"\nUsing voice: {voices.Item(voice_index).GetDescription()}")
        else:
            print(f"Warning: Voice index {voice_index} not found. Using default voice.")
        
        # Set voice properties
        speaker.Rate = rate
        speaker.Volume = volume
        
        # Convert text to speech
        speaker.Speak(text)
        
    except Exception as e:
        print(f"Error in text-to-speech conversion: {str(e)}")



# write prompts.py
file1 = "WelcomeToThePhyzAIProject.txt"


# Read first file
with open(file1, 'r', encoding='utf-8') as file1:
    content1 = file1.read()
        
# Convert text to speech (using first voice by default)
text_to_speech(content1)


            
#print(f"Successfully combined files into {output}")