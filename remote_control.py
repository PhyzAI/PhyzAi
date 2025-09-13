#TODO:Implement this in main via the TODO sections

# Handles input from remote control
import time
from pathlib import Path
from queue import Queue
from threading import Thread

import serial
from rich import print as rp


class ArduinoInput:
    CMD_LOW = b'l'
    CMD_HI = b'h'

    def __init__(self, port: str = 'COM4', baud: int = 9600, delay: float = 1.0, **kwargs):
        self.port = serial.Serial(
            port=port,
            baudrate=baud,
            timeout=0,  # nonblocking mode
            **kwargs
        )
        self.event_queue = Queue()

        rp(f'[blue][bold]Setting up serial port {port} [/]({baud} baud)[/]', end='', flush=True)
        # self.port.open()
        self.port.write(ArduinoInput.CMD_LOW)
        self.port.flush()
        rp('[blue]...[/]', end='', flush=True)
        time.sleep(delay)
        # dump whatever garbage is on the line
        self.port.reset_input_buffer()
        rp('[bold green] ok[/]')

    def step(self):
        while char := self.port.read():
            self.event_queue.put(char)

    def loop(self):
        while self.port.is_open:
            self.step()


def start_auto() -> Queue[bytes]:
    port_name = 'COM4'
    if Path('./port2').exists():
        rp(f'[yellow]Using Linux test port (local port2)[/]')
        port_name = './port2'
    try:
        port = ArduinoInput(port=port_name)
        arduino_thread = Thread(target=port.loop, daemon=True)
        arduino_thread.start()
        return port.event_queue
    except serial.SerialException as e:
        rp(f'[red]Setting up serial communication failed: {e}[/]')
        return Queue()  # forever empty



if __name__ == '__main__':
    q = start_auto()
    while 1:
        print(q.get())
