#!/usr/bin/env python3

import requests
import json
import re

url = "http://localhost:11434/api/chat"

with open("system_prompt.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()

with open("messages.json") as g:
    messages = json.load(g)

if len(messages) == 0:
    messages.insert(0, {
        "role": "system",
        "content": system_prompt})

def ollama_warmup():
    requests.post(url, json={"model": "gemma3:4b-it-q4_K_M", "messages": [{"role": "user", "content": "hi"}], "stream": False})

def nyx_response(user_input, q):

    messages.append(
        {
    "role": "user",
    "content": user_input})

    data = {
            "model": "gemma3:4b-it-q4_K_M",
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": 0.65,
                "top_p": 0.9,
                "repeat_penalty": 1.15,
                "num_predict": 256,
                "seed": 42
                }
            }

    response = requests.post(url, json=data, stream=True)
    print("Nyx: ", end='', flush=True)

    # Ollama sends responses in NDJSON [Newline Delimited JSON] format
    # for streaming (means each response or line is an independent JSON
    # object with a new line).
    # Standard JSON expects one valid object consisting of data under the
    # {} brackets.
    # response.iter_lines() will split each line in the incoming response
    # (which is the token itself) and it gets equal to line.
    assistance_response = ""
    buffer = ""
    for line in response.iter_lines():
        if line:
            chunk = json.loads(line)
            if "message" in chunk:
                print(chunk["message"]["content"], end='', flush=True)
                assistance_response += chunk["message"]["content"]
                buffer += chunk["message"]["content"]
                if re.search(r'[.!?]', buffer):
                    q.put(buffer.strip())
                    buffer = ""

    if buffer.strip():
        q.put(buffer.strip())
    q.put(None)

    messages.append({
        "role": "assistant",
        "content": assistance_response
    })
    
    with open("messages.json", "w") as h:
        json.dump(messages, h, indent=4)

    print()

exit_messages = ["/exit", "goodbye", "bye"]

#while True:
    #user_input = input("you: ")
    #if user_input.lower() in exit_messages:
        #break
    #gh0st_response(user_input)

#print()
