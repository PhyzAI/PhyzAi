import requests
from bs4 import BeautifulSoup
import os
import win32com.client

def read_website_text(url):
    # Send GET request to the website
    response = requests.get(url)
    
    # Create BeautifulSoup object to parse HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract all text from the webpage
    text = soup.get_text()
    
    # Clean up the text (remove extra whitespace)
    clean_text = ' '.join(text.split())

    # Remove all the text after the string "Meet the Blarts"
    clean_text = clean_text.split("Meet the Blarts", 1)[1]
    
    clean_text = clean_text.split("Get ready to explore the wonders of science with Thunk, Spin, Click, and Clack!", 1)[0]

    return clean_text

def list_available_voices():
    """
    List all available voices on the system with detailed information
    """
    try:
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        voices = speaker.GetVoices()
        
        print("\nAvailable voices:")
        print("-" * 50)
        for i, voice in enumerate(voices):
            print(f"Voice {i}:")
            print(f"  Name: {voice.GetDescription()}")
            print(f"  ID: {voice.GetId()}")
            print(f"  Language: {voice.GetLanguage()}")
            print(f"  Gender: {'Female' if 'female' in voice.GetDescription().lower() else 'Male'}")
            print("-" * 50)
            
        return voices
    except Exception as e:
        print(f"Error listing voices: {str(e)}")
        return None

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

# read blarts webpage
url = "https://rise4steam.org/the-blarts.html"
website_text = read_website_text(url)

# List available voices
list_available_voices()

# Convert text to speech (using first voice by default)
text_to_speech(website_text)

# Example of using different voices:
# text_to_speech(website_text, voice_index=1)  # Use second voice
# text_to_speech(website_text, voice_index=2)  # Use third voice
# text_to_speech(website_text, voice_index=0, rate=-5)  # Use first voice with slower speed

# write prompts.py
file1 = "mainprompt.txt"
file2 = "overrideprompt.txt"
output = "prompts.py"

# Read first file
with open(file1, 'r', encoding='utf-8') as file1:
    content1 = file1.read()
        
# Read second file
with open(file2, 'r', encoding='utf-8') as file2:
    content2 = file2.read()
        
# Combine the contents
combined_content = content1 + '                "Blarts are ' + website_text[1:] + '"' + "\n" + content2
        
# Write to output file
with open(output, 'w', encoding='utf-8') as output_file:
    output_file.write(combined_content)
            
#print(f"Successfully combined files into {output}")