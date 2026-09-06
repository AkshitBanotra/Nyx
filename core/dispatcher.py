#!/usr/bin/env python3

import subprocess
import psutil
import socket
import json
import requests
from shared import q1, q2, CATEGORY_MAP
from pathlib import Path
from core.registry import Registry
from core.PromptManager import PromptManager
from ollama_api import messages, url, streaming_response
from abc import ABC, abstractmethod
from datetime import datetime
from tts import tts_worker

###############################

message_path = Path(__file__).resolve().parent.parent / "messages.json"

################################

#user_message = messages[-2]["content"]

def response_trigger(message):
    runtime_messages = [
        {
            "role": "system",
            "content": message
        },
        {
            "role": "user",
            "content": messages[-2]["content"]
        }
    ]

    payload = {"model": "batiai/gemma4-e2b:q4", "messages": runtime_messages, "think": False, "stream": True}
    response = requests.post(url, json=payload)
    assistant_message = streaming_response(response, q1, None)
    tts_worker(q1)
    messages.append({
        "role": "assistant",
        "content": assistant_message})
    
    with open(message_path, "w") as f:
        json.dump(messages, f, indent=4)

###############################

class Intent(ABC):

    @abstractmethod
    def execute(self, argument):
        pass

class LaunchApp(Intent):

    def execute(self, argument):

        DB_PATH = Path(__file__).resolve().parent / "applications.db"
        registry = Registry(DB_PATH)
        registry.initialize()

        for one_app in argument.split():
            if one_app not in CATEGORY_MAP:
                app_search = registry.search_name(one_app)
                #print(f"App search result for '{one_app}': {app_search}")
                matched_apps = None
                if app_search is not None:
                    command = json.loads(app_search[3])
                    if app_search[4]:
                        subprocess.Popen(["alacritty", "-e", *command])
                    else:
                        subprocess.Popen(command)
            else:
                matched_apps = registry.search_category(one_app)
                if matched_apps is not None:
                    apps = []
                    for app in matched_apps:
                        name = app[1]
                        apps.append(name)
                    prompt = PromptManager()
                    response_trigger(prompt.category_context(apps))
                else:
                    fallback_message = """The user's request doesn't match any available app or category. Let them know you couldn't find a match and ask them to be more specific about what they want. If they say they don't want to open anything, drop it and continue the conversation as normal."""

                    response_trigger(fallback_message, user_message)

class SysInfo(Intent):

    def __init__(self):
        self.conv = (1024 ** 3)

    def cpu_info(self):
        
        cpu = None
        cpu = psutil.cpu_percent()
        cpu_usage = f"""
        type: cpu
        usage: {cpu:.0f}%
        """
        return cpu_usage
    
    def ram_info(self):
        
        ram = None
        ram_info = psutil.virtual_memory()
        ram_used = ram_info.used / self.conv
        ram_total = ram_info.total / self.conv
        ram_percent = ram_info.percent
        ram = f"""
        type: ram
        usage: {ram_used:.0f} GB
        total: {ram_total:.0f} GB
        usage_percent: {ram_percent:.0f}%
        """

        return ram

    def disk_info(self):

        disk = None
        disk_info = psutil.disk_usage('/')
        free_disk = disk_info.free / self.conv
        disk_used = disk_info.percent
        disk = f"""
        type: disk
        usage: {disk_used:.0f}%
        free space: {free_disk:.0f}
        """

        return disk

    def battery_info(self):

        battery = None
        battery_info = psutil.sensors_battery()
        if battery_info:
            if battery_info.power_plugged:
                battery = f"""
                type: battery
                current: {battery_info.percent:.0f}%
                charger: plugged in
                """
            else:
                battery = f"""
                type: battery
                current: {battery_info.percent:.0f}%
                charger: not plugged in
                """
        else:
            battery = f"No battery found on this device."

        return battery

    def vram_info(self):

        used = None
        total = None
        perc = None
        temp = None

        try:
            result = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,memory.total,temperature.gpu,utilization.gpu", "--format=csv,noheader,nounits"], capture_output=True, text=True, check=True)

            values = []
            for value in float(result.stdout.split(",")):
                values.append(value.strip())

            used, total, temp, perc = map(float, values)

            #vram = f"GPU Status → VRAM: {float(used) / 1024:.0f}GiB /{float(total) / 1024:.0f} GiB | Load: {perc} percent | Temp: {temp}°C"
            vram = f"""
            type: GPU VRAM
            used: {float(used) / 1024:.0f} GB
            total: {float(total) / 1024:.0f} GB
            Current load: {perc:.0f}%
            Current temperature: {temp:.0f} °C
            """
            return vram
        
        except FileNotFoundError:
            vram = "nvidia-smi was not found. NVIDIA drivers may not be installed."
            return vram
        except subprocess.CalledProcessError:
            vram = "Failed to retrieve the GPU status"
            return vram

    def temp_info(self):

        temps = psutil.sensors_temperatures()

        if "coretemp" in temps:
            for sensor in temps["coretemp"]:
                if sensor.label.lower() == "package id 0":
                    return f"""
                    type: CPU temperature
                    Current Temperature: {sensor.current}°C
                    """
        elif "k10temp" in temps:
            for sensor in temps["k10temp"]:
                if sensor.label == "Tctl":
                    return f"""
                    type: CPU Temperature
                    Current Temperature: {sensor.current} °C
                    """

    def time_info(self):

        current_time = None

        now = datetime.now()

        current_time = now.strftime("%I:%M %p")

        time = f"""
        type: time
        Current time: {current_time}
        """

        return time

    def date_info(self):

        current_date = None
        now = datetime.now()
        current_date = now.strftime("%A, %d %B %Y")
        date = f"""type: date
        Current Date: {current_date}
        """
        return date

    def hostname(self):

        hostname = None
        
        try:
            hostname = socket.gethostname()
            hname = f"""
            type: Computer name
            name: {hostname}
            """
            return hname
        except Exception:
            hostname = "Unable to retrieve hostname."
            return hostname

    def execute(self, argument):
        
        sys_info = {
            "cpu": self.cpu_info,
            "ram": self.ram_info,
            "vram": self.vram_info,
            "battery": self.battery_info,
            "disk": self.disk_info,
            "temperature": self.temp_info,
            "hostname": self.hostname,
            "time": self.time_info,
            "date": self.date_info
        }

        #results = {}
        #for key in sys_info:
            #results[key] = None

        results = {}
        for one_info in argument.split():
            if one_info in sys_info:
                results[one_info] = sys_info[one_info]()
            else:
                results[one_info] = None
        #print(results)
        
        prompt = PromptManager()
        response_trigger(prompt.system_context(results))

def intent_route(q2):

    intent_router = {
        "[LAUNCH]": LaunchApp(),
        "[SYSTEM]": SysInfo()
    }

    while True:

        text = q2.get()

        if text is None:
            break
        
        action, argument = text.split(maxsplit=1)
        
        if action in intent_router:
            intent = intent_router.get(action)
            intent.execute(argument)
