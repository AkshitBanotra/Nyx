#!/usr/bin/env python3

import configparser
from pathlib import Path

directory = Path('/usr/share/applications')
desktop_files = directory.rglob('*.desktop')

def scanner():
    application = []
    for file in desktop_files:
        config = configparser.ConfigParser(interpolation=None)
        config.optionxform = str
        config.read(file, encoding="utf-8")
        return config

print(scanner())
