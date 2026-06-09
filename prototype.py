#!/usr/bin/env python3

from subprocess import run, Popen, DEVNULL
import re
import random

apps = [ "browser", "brave" ]
run(' echo "gh0st: Welcome ${USER}!" ', shell=True)
text = input(">> ")

#youtube = ["yt", "youtube" ]
#text = input(">> ")
#if any(site in text for site in youtube):
    #Popen([ "xdg-open", "https://www.youtube.com" ])

if any(app in text for app in apps):
    Popen(["xdg-open", "https://www.google.com"], stdout=DEVNULL, stderr=DEVNULL)
else:
    print("gh0st: Couldn't figure out what you meant.")

text = input(">> ")

dim = [ "dim", "low bright" ]
DarkOn = [ "on the nightlight", "dark", "too bright", "nightlight on", "on nightlight" ]
DarkOff = [ "too dark", "nightlight off", "bright", "off the nightlight", "off nightlight" ]

if any(night in text for night in DarkOn):
    run(["redshift", "-x"])
    run(["redshift", "-O", "3500"])
    run(["brightnessctl", "set", "15%"])

if any(day in text for day in DarkOff):
    run([ "redshift", "-x" ])
#else:
    #print("gh0st: Couldn't figure out what you meant.")
