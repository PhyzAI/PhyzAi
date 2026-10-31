import threading

is_speaking = threading.Event()
is_listening = threading.Event()

def set_speaking_status(status: bool):
    if status:
        is_speaking.set()
    else:
        is_speaking.clear()

def check_if_speaking():
    return is_speaking.is_set()



def set_listening_status(status: bool):
    if status:
        is_listening.set()
    else:
        is_listening.clear()

def check_if_listening():
    return is_listening.is_set()
