#!/bin/python3

import os
import time
import datetime
import json
import requests
import subprocess
import random

print(random.randrange(10000))

def getToken():
    if not os.path.exists("token"):
        print("ERR: No token file found.")
        print("Please create a file called 'token' within the same directory as this script and paste your ESP API token in it.")
        exit()

    with open("token", "r") as f:
        token = f.read()
        if token == "":
            print("ERR: Token file is empty.")
            exit()

        return token if token != "" else None

def get_latest_data():
    pass

def writeData(data):
    pass