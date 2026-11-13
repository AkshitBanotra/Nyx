#!/usr/bin/env python3

from resources.resource_manager import ResourceManager, Timer
import subprocess
import json
#from core.PromptManager import PromptManager
import threading
from pathlib import Path
import shared

json_path = Path(__file__).resolve().parent.parent / "config.json"

with open(json_path, "r") as f:
    data = json.load(f)


sound_path = Path(__file__).resolve().parent.parent / "sounds" / "ux_sound_4.mp3"

def resource_manager():

    resource_manager = ResourceManager()
    timer = Timer()
    resource_high = resource_manager.res_state()

    def res_timer_cancel():

        if not resource_high:
            timer.cancel()

    cancel_timer = threading.Thread(target=res_timer_cancel)

    cancel_timer.start()

    if resource_high:
        print("Resources are high now!")
        timer.start(5)
        data["llm_active"] = False
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)
        
        #prompt = PromptManager()
        #trigger = "System resources have crossed the configured threshold."
        #auto_trigger(prompt.res_pressure_context, trigger)
        subprocess.run(["notify-send", "[NYX]", "Sleeping..."])
        subprocess.run(["paplay", sound_path])
        subprocess.run(["ollama", "stop", shared.model])
        subprocess.run(["systemctl", "--user", "stop", "Nyx.service"])


resource_manager()
