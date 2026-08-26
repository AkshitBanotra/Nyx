#!/usr/bin/env python3

import socket
import os
import threading
from os import environ
from ollama_api import ollama_warmup, nyx_response
from tts import tts_warmup, tts_worker
import re
from animation import text_animation
import shared
import time
import stt
import core.dispatcher
import subprocess

###########################

home = environ["HOME"]
sound_path1 = f"{home}/gh0st/sounds/ux_sound_1.mp3"
sound_path2 = f"{home}/gh0st/sounds/ux_sound_2.mp3"

###########################

socket_path = "/tmp/my_socket"

# Remove old socket file if it exists.

try:
    os.unlink(socket_path)
except FileNotFoundError:
    pass

# Create Unix domain socket.

server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Bind socket to filesystem path
server.bind(socket_path)

# Listen for connections

server.listen(1)

# Accept a client.

#connection, _ = server.accept()

def llm_toggle():
    try:
        while True:

            connection, _ = server.accept()
            print("Client connected...")

            data = connection.recv(1024)
            if not data:
                break

            if data == b'LLM_TOGGLE':
                print("Data recieved...")
                subprocess.run(["notify-send", "[NYX]", "Listening..."])
                subprocess.run(["paplay", sound_path2])
                shared.llm_listen = True
                print("LLM_LISTEN STATE: ", str(shared.llm_listen))

    finally:
        connection.close()
        server.close()

        # Remove socket file
        try:
            os.unlink(socket_path)
        except FileNotFoundError:
            pass

###########################

def clear_screen():
    #\033[H moves the cursor to the top left; \033[2J clears the entire screen
    print("\033[H\033[2J", end="")

##########################

subprocess.run(["notify-send", "[Nyx]", "Initializing..."])
subprocess.run(["paplay", sound_path1])
time.sleep(0.5)
subprocess.run(["notify-send", "[Nyx]", "Loading models..."])
subprocess.run(["notify-send", "[Nyx]", "Warming up..."])

ollama_warmup()
tts_warmup()

subprocess.run(["notify-send", "[Nyx]", "ready."])
subprocess.run(["paplay", sound_path1])
time.sleep(1)

exit_messages = [ "/exit", "goodbye", "bye" ]

stt_thread = threading.Thread(
        target=stt.stt_start,
        daemon=True
        )

uds_thread = threading.Thread(
        target=llm_toggle,
        daemon=True
        )

stt_thread.start()
uds_thread.start()

clear_screen()

while True:
    speech = stt.speech_queue.get()
    user_input = f"you:{speech}"
    #user_input = input("you: ")
    print(user_input)
    if any(message in user_input for message in exit_messages):
        break
    t1 = threading.Thread(target=nyx_response, args=(user_input, shared.q1, shared.q2))
    t2 = threading.Thread(target=tts_worker, args=(shared.q1,))
    t3 = threading.Thread(target=core.dispatcher.intent_route, args=(shared.q2,))

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

print()
