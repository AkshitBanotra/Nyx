#!/usr/bin/env python

result = {
        "key": "Value",
        "Value": "Key :D",
        "lol": "What?"
}

info_fetch = {}
for i in result:
    info_fetch[i] = result[i]
    print(info_fetch[i])
