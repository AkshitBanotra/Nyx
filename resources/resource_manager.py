#!/usr/bin/env python3

import psutil
import json
import subprocess
from pathlib import Path
import time
import threading
from filelock import FileLock

class Timer:

    def start(self, duration):
        
        self.duration = duration

        self.running = True
        i = self.duration
        while self.running:

            #print(f"\rTime left: {i}")
            if i <= 0:
                break

            i -= 1
            time.sleep(1)

    def cancel(self):

        self.running = False

    def test_cancel(self):
        input()
        self.cancel()

class ResourceManager:
    
    def __init__(self):
        
        parent = Path(__file__).resolve().parent.parent

        self.json_path = parent / "config.json"
        self.lock = FileLock(parent / "config.json.lock")
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

    def res_state(self):

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
    print(resource_manager.res_state())
    timer = Timer()
    thread = threading.Thread(target=timer.test_cancel)
    thread.start()
    timer.start(5)
