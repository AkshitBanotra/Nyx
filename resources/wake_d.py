#!/usr/bin/env python3

import json
from resources.resource_manager import ResourceManager
from pathlib import Path

#########################

parent = Path(__file__).resolve().parent.parent
json_path = parent / "config.json"
sound_path = parent / "sounds" / "ux_sound_5.mp3"

resource_manager = ResourceManager()
resource_high = resource_manager.res_state()

with open(json_path, "r") as f:
    data = json.load(f)

def res_timer_cancel():
    
    if resource_high:
        timer.cancel()

cancel_timer = threading.Thread(target=res_timer_cancel)

cancel_timer.start()

if not resource_high:
    if not data["llm_active"]:
        
        data["llm_active"] = True
        
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)

        subprocess.run(["notify-send", "[NYX]", "Waking up..."])
        subprocess.run(["paplay", sound_path])
        subprocess.run(["systemctl", "--user", "start", "Nyx.service"])
