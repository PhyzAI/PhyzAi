import requests
from bs4 import BeautifulSoup
import os
import subprocess

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
    List all available voices in Festival
    """
    try:
        # Get list of available voices using festival -i
        result = subprocess.run(['wsl', 'festival', '-i', '--tts'], capture_output=True, text=True)
        voices = []
        
        # Parse the output to get voice names
        for line in result.stdout.split('\n'):
            if 'voice_' in line:
                voices.append(line.strip())
        
        print("\nAvailable Festival voices:")
        print("-" * 50)
        for i, voice in enumerate(voices):
            print(f"Voice {i}: {voice}")
        print("-" * 50)
            
        return voices
    except Exception as e:
        print(f"Error listing voices: {str(e)}")
        return None

def text_to_speech(text, voice_name="kal_diphone", rate=1.0, volume=1.0):
    """
    Convert text to speech using Festival
    
    Args:
        text (str): Text to convert to speech
        voice_name (str): Name of the voice to use (default: kal_diphone)
        rate (float): Speech rate (0.5 to 2.0, default: 1.0)
        volume (float): Volume level (0.0 to 1.0, default: 1.0)
    """
    try:
        # Create a temporary file to store the text
        with open('temp.txt', 'w', encoding='utf-8') as f:
            f.write(text)
        
        # Festival command with voice selection and parameters
        cmd = [
            'wsl',
            'festival',
            '--tts',
         #   '--voice', voice_name,
         #   '--rate', str(rate),
         #   '--volume', str(volume),
            'temp.txt'
        ]
        
        # Run Festival
        subprocess.run(cmd)
        
        # Clean up temporary file
        os.remove('temp.txt')
        
    except Exception as e:
        print(f"Error in text-to-speech conversion: {str(e)}")
        if os.path.exists('temp.txt'):
            os.remove('temp.txt')

# read blarts webpage
url = "https://rise4steam.org/the-blarts.html"
website_text = read_website_text(url)

print(f"Received context") # DEBUG
# List available voices
list_available_voices()

print(f"Listed voices") # DEBUG

# Convert text to speech (using kal_diphone voice by default)
#text_to_speech(website_text)

# Example of using different voices and parameters:
# text_to_speech(website_text, voice_name="bdl", rate=1.2)  # Use bdl voice with faster speed
# text_to_speech(website_text, voice_name="rms", rate=0.8)  # Use rms voice with slower speed

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

print(f"calling TTS") # DEBUG
text_to_speech(combined_content, voice_name="bdl", rate=1.2)  # Use bdl voice with faster speed

# Write to output file
with open(output, 'w', encoding='utf-8') as output_file:
    output_file.write(combined_content)
            
#print(f"Successfully combined files into {output}")