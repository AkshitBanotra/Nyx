import threading
import queue
from ollama_api import ollama_warmup, nyx_response
from tts import tts_warmup, tts_worker
import re
from animation import text_animation
import time

q = queue.Queue()

def clear_screen():
    # \033[H moves the cursor to the top left; \033[2J clears the entire screen
    print("\033[H\033[2J", end="")

text_animation("[Nyx] initializing...")
time.sleep(0.5)
text_animation("[Nyx] loading models...")
text_animation("[Nyx] warming up...")

ollama_warmup()
tts_warmup()

text_animation("[Nyx] ready.")

exit_messages = [ "/exit", "goodbye", "bye" ]

clear_screen()

while True:
    user_input = input("you: ")
    if user_input.lower() in exit_messages:
        break
    t1 = threading.Thread(target=nyx_response, args=(user_input, q))
    t2 = threading.Thread(target=tts_worker, args=(q,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()


print()
