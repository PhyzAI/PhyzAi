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

def main():
    serialObj.timeout = 0

    print("recieved:" + serialObj.read().decode('ascii'))

    time.sleep(0.1)

while True:
    main()