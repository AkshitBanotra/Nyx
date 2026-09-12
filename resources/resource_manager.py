#!/usr/bin/env python3

import psutil
import json
import subprocess
from pathlib import Path
from core.PromptManager import PromptManager
from threading import Timer

class ResourceManager:
    
    def __init__(self):
        
        parent = Path(__file__).resolve().parent.parent

        self.json_path = parent / "config.json"
        self.sound_path1 = parent / "sounds" / "ux_sound_4.mp3"
        self.sound_path2 = parent / "sounds" / "ux_sound_5.mp3"
        self.threshold_ram = 75
        self.threshold_vram = 95
        self.threshold_cpu = 80

    def current_cpu(self):

        cpu_usage = psutil.cpu_percent()

        return cpu_usage
    
    def current_ram(self):

        ram_info = psutil.virtual_memory()
        ram_used = ram_info.percent

        return ram_used
    
    def current_vram(self):

        result = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,memory.total", "--format=csv,noheader,nounits"], capture_output=True, text=True, check=True)

        values = []
        for value in result.stdout.split(","):
            values.append(value.strip())

        used, total = map(float, values)

        vram_perc = (used / total) * 100

        return vram_perc

    def res_pressure_high_response(self, data):

        data["res_high"]  = True
        
        with open(self.json_path, "w") as f:
            json.dump(data, f, indent=4)
        return data["res_high"]
            
    def res_pressure_low_response(self, data):

        data["res_high"]  = False
        with open(self.json_path, "w") as f:
            json.dump(data, f, indent=4)
        return data["res_high"]

    def res_state_change(self):

        with open(self.json_path, "r") as f:
            data = json.load(f)

        if (
                self.current_cpu() >= self.threshold_cpu
                or self.current_ram() >= self.threshold_ram
                or self.current_vram() >= self.threshold_vram
        ):
            return self.res_pressure_high_response(data)
        else:
            if not data["llm_active"]:
                return self.res_pressure_low_response(data)

if __name__ == "__main__":
    resource_manager = ResourceManager()
    print(resource_manager.res_state_change())
