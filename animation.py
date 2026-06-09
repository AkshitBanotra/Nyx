#!/usr/bin/env python3

import time

################################

def text_animation(text):
    textlen = len(text)

    i = 0
    while i < textlen:
        print(f"{text[i]}",end='', flush=True)
        i = i + 1
        time.sleep(0.045)

    print('')

#text_animation("Hello!")
#text_animation("Something...")
