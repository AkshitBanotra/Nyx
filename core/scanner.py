#!/usr/bin/env python3

import configparser
from pathlib import Path

class Scanner:

    def scan(self):
        directory = Path('/usr/share/applications')
        desktop_files = directory.rglob('*.desktop')
        return desktop_files

class Parser:

    def parse(self, file):
        config = configparser.ConfigParser(interpolation=None) # Creates the parser object
        config.optionxform = str # Prevent configparser from lowercasing keys.
        config.read(file, encoding="utf-8")
        if "Desktop Entry" in config:
            entry = config["Desktop Entry"]
            type = entry.get("Type")
            hidden = entry.getboolean("Hidden", fallback=False)
            nodisplay = entry.getboolean("NoDisplay", fallback=False)
            raw_exec_command = entry.get("Exec")

            if type != "Application":
                return None
            if raw_exec_command is None:
                return None
            if nodisplay:
                return None
            if hidden:
                return None

            command_parts = raw_exec_command.split()
            exec_command = []
            for part in command_parts:
                if part.startswith("%"):
                    continue
                exec_command.append(part)

        name = entry.get("Name")
        categories = entry.get("Categories")
        is_terminal = entry.getboolean("Terminal", fallback=False)

        return name, exec_command, categories, is_terminal

class Data(Parser):
    def app_data(self):
        scanner = Scanner()
        parser = Parser()
        apps = []
        for file in scanner.scan():
            result = parser.parse(file)

            if result is None:
                continue

            Name, Command, Categories, Terminal = result
            
            data = {
                    "name": Name,
                    "categories": Categories,
                    "command": Command,
                    "terminal": Terminal
                    }

            apps.append(data)

        return apps

if __name__ == "__main__":
    Data = Data()
    print(Data.app_data())
