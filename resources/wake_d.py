#!/usr/bin/env python3

import json
from resource_manager import ResourceManager, Timer
from pathlib import Path
import threading
import subprocess
import time
from filelock import FileLock

#########################

parent = Path(__file__).resolve().parent.parent
sound_path = parent / "sounds" / "ux_sound_5.mp3"

resource_manager = ResourceManager()
timer = Timer()
#resource_high = resource_manager.res_state()

lock = FileLock(parent/"config.json.lock")

def res_timer_cancel():

    while True:
        if resource_manager.res_state():
            timer.cancel()
    time.sleep(1)

cancel_timer = threading.Thread(target=res_timer_cancel)

cancel_timer.start()

while True:
    if not resource_manager.res_state():

        with lock:            
            with open(parent / "config.json", "r") as f:
                data = json.load(f)
   
            if not data["llm_active"]:
                timer.start(10)
                #wake = True
                print("Resources are low now!")
                subprocess.run(["notify-send", "[NYX]", "Waking up..."])
                subprocess.run(["paplay", sound_path])
                subprocess.run(["systemctl", "--user", "start", "Nyx.service"])
                
    time.sleep(1)
