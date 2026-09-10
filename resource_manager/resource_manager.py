#!/usr/bin/env python3

import psutil
import requests
import subprocess
from core.PromptManager import PromptManager
import shared
from threading import Timer
from os import environ
import json
from pathlib import Path
from ollama_api import streaming_response
from tts import tts_worker

#######################

home = environ["HOME"]
json_path = Path(__file__).resolve().parent.parent / "config.json"
sound_path1 = f"{home}/gh0st/sounds/ux_sound_4.mp3"
sound_path2 = f"{home}/gh0st/sounds/ux_sound_5.mp3"

######################

with open(json_path, "r") as f:
    data = json.load(f)
    
######################

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

threshold_ram  = 75
threshold_vram = 82

def current_ram():
    
    conv = (1024 ** 3)

    ram_info = psutil.virtual_memory()
    ram_used = ram_info.total / conv
    
    return ram_used

def current_vram():

    result = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"], capture_output=True, text=True, check=True)

    values = []
    for value in result.stdout.split(","):
        values.append(value.strip())

    used, total = map(float, values)

    vram_perc = (used / total) * 100

    return vram_perc

def res_pressure_high_response():
    
    prompt = PromptManager()
    trigger = "System resources have reached the threshold. Generate a brief autonomous spoken response to this situation."
    auto_trigger(prompt.res_pressure_context(), trigger)
    subprocess.run(["notify-send", "[NYX]", "Sleeping..."])
    subprocess.run(["paplay", sound_path1])
    subprocess.run(["systemctl", "--user", "stop", "Nyx.service"])
    subprocess.run(["ollama", "stop", shared.model])
    data["llm_active"] = False
    with open(json_path, "w") as f:
        json.dump(data, f, indent=4)
    print(data["llm_active"])

def res_pressure_low_response():

    subprocess.run(["notify-send", "[NYX]", "Waking up..."])
    subprocess.run(["paplay", sound_path2])
    subprocess.run("systemctl", "--user", "start", "Nyx.service")

timer_1 = Timer(5, res_pressure_high_response)
timer_2 = Timer(15, res_pressure_low_response)

while True:
    if current_ram() >= threshold_ram or current_vram() >= threshold_vram:
        timer_1.start()
        timer_2.cancel()
    else:
        #print(data["llm_active"])
        if not data["llm_active"]:
            timer_2.start()
            timer_1.cancel()
