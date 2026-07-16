#!/usr/bin/env python3

import configparser
from pathlib import Path

directory = Path('/usr/share/applications')
desktop_files = directory.rglob('*.desktop')

for file in desktop_files:
    config = configparser.ConfigParser(interpolation=None) # Creates the parser object.
    config.optionxform = str # Prevent configparser from lowercasing keys.
    config.read(file, encoding="utf-8")

    if "Desktop Entry" in config:
        entry = config["Desktop Entry"]

        type = entry.get("Type")
        hidden = entry.get("Hidden")
        nodisplay = entry.get("NoDisplay")
        exec_command = entry.get("Exec")

        if type != "Application":
            continue
        if exec_command is None:
            continue
        if nodisplay:
            continue
        if hidden:
            continue

        command_parts = exec_command.split()
        clean_parts = []
        for part in command_parts:
            if part.startswith("%"):
                continue
            clean_parts.append(part)

        name = entry.get("Name")
        icon = entry.get("Icon")
        is_terminal = entry.getboolean("Terminal", fallback=False)

        print(f"App name: {name}")
        print(f"Command: {clean_parts}")
        print(f"Icon: {icon}")
        print(f"Terminal: {is_terminal}")
