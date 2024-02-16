import pyfirmata
import serial
import time
import keyboard

serialObj = serial.Serial('COM3')
serialObj.baudrate = 9600
serialObj.bytesize = 8
serialObj.parity = 'N'
serialObj.stopbits = 1
time.sleep(3)

while True :
    print("press 1 for head 2 for left arm 3 for right arm")
    key = keyboard.read_key()
    if key == '1':
        serialObj.write(b"1")
        time.sleep(1)
    if key == '2':
        serialObj.write(b"2")
        time.sleep(1)
    if key == '3':
        serialObj.write(b"3")
        time.sleep(1)
#time.sleep(0.2)
#board.digital[13].write(0)
#time.sleep(0.2)