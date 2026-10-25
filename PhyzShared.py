import threading

is_speaking = threading.Event()

def set_speaking_status(status: bool):
    if status:
        is_speaking.set()
    else:
        is_speaking.clear()

def check_if_speaking():
    return is_speaking.is_set()
