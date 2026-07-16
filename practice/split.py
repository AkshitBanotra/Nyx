#!/usr/bin/env python3

import numpy as np
import sounddevice as sd
import time as sleep
import threading

threading_event = threading.Event()

fake_audio = np.zeros(2500)

threading_event.clear()
def interruption():
    any_key = input("Press any key to break the loop...")
    threading_event.set()

print("Loop started...")

def split():
    start = 0
    while ( start < len(fake_audio)):
        end = start + 2400
        piece = fake_audio[start:end]
        print("audio started... (even though silent one :D)")
        print(str(start) + " to " + str(end) + ".")
        sd.play(piece, 24000)
        sd.wait()
        if threading_event.is_set():
            print("Interruption occured...")
            break
        start = end

t1 = threading.Thread(target=split)
t2 = threading.Thread(target=interruption)

t1.start() 
t2.start()

t1.join()
t2.join()
