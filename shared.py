#!/usr/bin/env python3

import queue

##################

q1 = queue.Queue()
q2 = queue.Queue()

llm_busy = False
tts_playing = False

#intent_message = q2.get()

INTENTS = ("[LAUNCH]", "[SYSTEM]")

CATEGORY_MAP = {
        "browser": "WebBrowser",
        "terminal": "TerminalEmulator",
        "editor": "TextEditor",
        "ide": "Development",
        "music": "Player",
        "video": "AudioVideo",
        "file manager": "FileManager",
        "settings": "Settings",
}

