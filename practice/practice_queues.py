#!/usr/bin/env python3

import queue

q = queue.Queue()

sentences = [
        "Maybe you want performance mode.",
        "Should I change it?",
        "Battery is at 20 percent."
        ]


# simultate to ollama putting chunks in
for sentence in sentences:
    q.put(sentence)

# simulate tts consuming them
while not q.empty():
    print(q.get())
