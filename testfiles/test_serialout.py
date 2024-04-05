import serial
import time
# init communicatio with arduino
LOW_COMMAND = bytes('l', "utf-8")
HIGH_COMMAND = bytes('h', "utf-8")

if __name__ == "__main__":
    serialObj = serial.Serial('COM4')
    serialObj.baudrate = 9600
    serialObj.bytesize = 8
    serialObj.parity = 'N'
    serialObj.stopbits = 1
    serialObj.timeout = None
    while True:
        serialObj.write(LOW_COMMAND)
        serialObj.flush()
        time.sleep(1)
        serialObj.write(HIGH_COMMAND)
        serialObj.flush()
        time.sleep(1)
