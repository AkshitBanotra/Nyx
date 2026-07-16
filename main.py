import threading
import queue
from ollama_api import ollama_warmup, nyx_response
from tts import tts_warmup, tts_worker
import re
from animation import text_animation
import time
import stt

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
time.sleep(1)

exit_messages = [ "/exit", "goodbye", "bye" ]

stt_thread = threading.Thread(
        target=stt.stt_start,
        daemon=True
        )

stt_thread.start()

clear_screen()

while True:
    speech = stt.speech_queue.get()
    user_input = f"you:{speech}"
    print(user_input)
    if speech.lower() in exit_messages:
        break
    t1 = threading.Thread(target=nyx_response, args=(user_input, q))
    t2 = threading.Thread(target=tts_worker, args=(q,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()


print()
