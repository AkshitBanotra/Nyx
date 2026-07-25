#!/usr/bin/env python3

import requests
import json
import re
from shared import llm_busy
from core.PromptManager import PromptManager

#############################

INTENTS = ("[LAUNCH]", "[SYSTEM]")

url = "http://localhost:11434/api/chat"
prompt = PromptManager()

with open("messages.json") as g:
    messages = json.load(g)

if len(messages) == 0:
    messages.insert(0, {
                    "role": "system",
                    "content": prompt.base_prompt()})
    messages.insert(1, {
                    "role": "system",
                    "content": ""})
    messages.insert(2, {
                    "role": "system",
                    "content": ""})

def ollama_warmup():
    requests.post(url, json={"model": "gemma3:4b-it-q4_K_M", "messages": [{"role": "user", "content": "hi"}], "stream": False})

def streaming_response(response, q1, q2=None):

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
                    if buffer.startswith(INTENTS):
                        if q2 is not None:
                            q2.put(buffer.strip())
                    else:
                        q1.put(buffer.strip())
                    buffer = ""
    
    if buffer.strip():
        if buffer.startswith(INTENTS):
            if q2 is not None:
                q2.put(buffer.strip())
            else:
                q1.put(buffer.strip())
    q1.put(None)
    if q2 is not None:
        q2.put(None)

    return assistance_response

def nyx_response(user_input, q1, q2):

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

    llm_busy = True
    response = requests.post(url, json=data, stream=True)

    assistance_response = streaming_response(response, q1, q2)

    messages.append({
        "role": "assistant",
        "content": assistance_response
    })
    
    with open("messages.json", "w") as h:
        json.dump(messages, h, indent=4)

    llm_busy = False
    print()