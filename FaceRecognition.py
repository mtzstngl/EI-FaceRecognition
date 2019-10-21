#!/bin/env python3
# Simple example that converts a python dict object to json
import sys
import time
import json
import random

# Python dict object
status = {
    "name":  None,
    "emotion": None,
    "index": -1 # The index of the Person
}

name = [None, "Peter", "Max"]
emotion = [None, "happy", "angry", "sad", "neutral"]

random.seed()

while True:
    status["name"] = name[random.randint(0, 2)] 
    status["emotion"] = emotion[random.randint(0, 4)]
    print(json.dumps(status))
    time.sleep(10)
