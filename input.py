# Handles input from remote control
import time
from queue import Queue
from threading import Thread

import serial
from rich import print as rp


class ArduinoInput:
    CMD_LOW = b'l'
    CMD_HI = b'h'

    def __init__(self, port: str = 'COM4', baud: int = 9600, delay: float = 1.0):
        self.port = serial.Serial(
            port=port,
            baudrate=baud,
            timeout=0  # nonblocking mode
        )
        self.event_queue = Queue()

        rp('[green][bold]Setting up serial port[/] {port} {baud}baud[/]', end='', flush=True)
        self.port.open()
        self.port.write(ArduinoInput.CMD_LOW)
        self.port.flush()
        rp('[green]...[/]', end='', flush=True)
        time.sleep(delay)
        # dump whatever garbage is on the line
        self.port.reset_input_buffer()
        rp('[bold green]done[/]')

    def step(self):
        while char := self.port.read():
            self.event_queue.put(char)

    def loop(self):
        while self.port.is_open:
            self.step()


def start() -> Queue[bytes]:
    port = ArduinoInput()
    arduino_thread = Thread(target=port.loop, daemon=True)
    arduino_thread.start()
    return port.event_queue
