#!/usr/bin/env python3

import os
import socket
from pathlib import Path
import threading
import json
import requests
from ollama_api import ollama_warmup, streaming_response, nyx_response, messages
from tts import tts_warmup, tts_worker
from pathlib import Path
import re
from animation import text_animation
import shared
import time
import stt
import core.dispatcher
from core.PromptManager import PromptManager
from resources.resource_manager import Timer, ResourceManager
import subprocess
from datetime import datetime
import json
from filelock import FileLock

###########################

parent = Path(__file__).resolve().parent

sound_path1 = parent / "sounds" / "ux_sound_1.mp3"
sound_path2 = parent / "sounds" / "ux_sound_2.mp3"
sound_path3 = parent / "sounds" / "ux_sound_3.mp3"
sound_path4 = parent / "sounds" / "ux_sound_4.mp3"
json_path = parent / "config.json"

lock = FileLock(parent/"config.json.lock")

#######################################

def auto_trigger(message, trigger):
    runtime_message = [
        {
            "role": "system",
            "content": message
        },
        {
            "role": "user",
            "content": trigger
        }
    ]
    payload = {"model": "batiai/gemma4-e2b:q4", "messages": runtime_message, "think": False, "stream": True}
    response = requests.post(shared.url, json=payload)
    print(response)
    assistant_message = streaming_response(response, shared.q1, None)
    tts_worker(shared.q1)

##########################################

def time_date_info():

    now = datetime.now()
    current_date = now.strftime("%d %B %Y")
    current_day = now.strftime("%A")
    current_time = now.strftime("%I:%M %p")

    time_data = {
        "date": current_date,
        "day": current_day,
        "time": current_time
    }

    return time_data

#########################################

def llm_toggle():
    
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

    try:
        while True:
            connection, _ = server.accept()
            print("Client connected...")

            data = connection.recv(1024)
            if not data:
                break

            if data == b'LLM_TOGGLE':
                print("Data recieved...")
                shared.llm_listen = not shared.llm_listen
                if shared.llm_listen:
                    subprocess.run(["notify-send", "[NYX]", "Listening..."])
                    subprocess.run(["paplay", sound_path2])
                else:
                    subprocess.run(["notify-send", "[NYX]", "Going Silent..."])
                    subprocess.run(["paplay", sound_path3])
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

def resource_manager():

    resource_manager = ResourceManager()
    timer = Timer()
    #lock = threading.Lock()
    #resource_high = resource_manager.res_state()

    def res_timer_cancel():
            while True:
                if not resource_manager.res_state():
                    timer.cancel()
            time.sleep(1)

    cancel_timer = threading.Thread(target=res_timer_cancel)

    cancel_timer.start()
    while True:
        if resource_manager.res_state():
            with lock:
                
                with open(parent / "corows = cursor.fetchall()nfig.json", "r") as f:
                    dict_data = json.load(f)
                
                timer.start(5)
                data["llm_active"] = False
                with open(json_path, "w") as f:
                    json.dump(dict_data, f, indent=4)

                prompt = PromptManager()
                trigger = "Resources have crossed the threshold values. Follow your instructions. You don't have to give troubleshoot etc. Just reply like Nyx, in that personality, that resources have crossed threshold values etc."
                auto_trigger(prompt.res_pressure_context(), trigger)
                subprocess.run(["notify-send", "[NYX]", "Sleeping..."])
                subprocess.run(["paplay", sound_path4])
                subprocess.run(["ollama", "stop", shared.model])
                subprocess.run(["systemctl", "--user", "stop", "Nyx.service"])

        time.sleep(1)
##########################

# When this main process starts, it'll turn the llm_active state to true...

with lock:
    with open(json_path, "r") as f:
        data = json.load(f)

    data["llm_active"] = True

    with open(json_path, "w") as f:
        json.dump(data, f, indent=4)

print(data["llm_active"])

subprocess.run(["notify-send", "[Nyx]", "Initializing..."])
subprocess.run(["paplay", sound_path1])
time.sleep(0.5)
subprocess.run(["notify-send", "[Nyx]", "Loading models..."])
subprocess.run(["notify-send", "[Nyx]", "Warming up..."])

ollama_warmup()
tts_warmup()

subprocess.run(["notify-send", "[Nyx]", "ready."])
subprocess.run(["paplay", sound_path1])

time.sleep(0.5)

# For startup greet.

prompt = PromptManager()
greet = "Hello."
auto_trigger(prompt.greet(time_date_info()), greet)

########################

#exit_messages = [ "/exit", "goodbye", "bye" ]

stt_thread = threading.Thread(
        target=stt.stt_start,
        daemon=True
        )

uds_thread = threading.Thread(
        target=llm_toggle,
        daemon=True
        )

res_manager_thread = threading.Thread(
        target=resource_manager,
        daemon=True
        )

stt_thread.start()
uds_thread.start()
res_manager_thread.start()

clear_screen()

while True:
    speech = stt.speech_queue.get()
    user_input = f"you:{speech}"
    #user_input = input("you: ")
    print(user_input)
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
