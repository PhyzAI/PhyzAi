# Example: Using threading to run two functions in parallel
import threading
from io import BytesIO
import time

def print_numbers():
    for i in range(10):
        print(f"Number: {i}")
        time.sleep(1)

def print_letters():
    for letter in "abcdefgh":
        print(f"Letter: {letter}")
        time.sleep(1)

if __name__ == "__main__":
    # Start two threads
    t1 = threading.Thread(target=print_numbers)
    t2 = threading.Thread(target=print_letters)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    #main()