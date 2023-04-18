#!/bin/python3

import os
import sys
import time
import datetime
import json
import requests
import random

CONFIG = {
    "id": "region-x-area",
    "name": "YOURAREA (x)",
    "region": "YourRegion",
    "refresh": 30, # How often to refresh the data in minutes
}

def getToken():
    token_file = os.path.dirname(os.path.realpath(__file__)) + os.sep + "token"

    if not os.path.exists(token_file):
        print("ERR: No token file found.")
        print("Please create a file called 'token' within the same directory as this script and paste your ESP API token in it.")
        exit()

    with open(token_file, "r") as f:
        token = f.read()
        if token == "":
            print("ERR: Token file is empty.")
            exit()

        return token if token != "" else None


# Cache + Return the latest loadshedding data for the area
# Data cache is refreshed every CONFIG["refresh"] minutes
def getData(token):
    cache_file = os.path.dirname(os.path.realpath(__file__)) + os.sep + "cache.json"
    cache = None

    # Check if we have a cached version of the data
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            try:
                raw = f.read()

                if raw != "":
                    cache = json.loads(raw)
                    if cache["timestamp"] + (CONFIG["refresh"] * 60) < time.time():
                        return cache

            except:
                pass # Ignore errors, we'll just try get the data again

    # Get the latest data
    try:
        resp = requests.get(
            "https://developer.sepush.co.za/business/2.0/area?id={}".format(CONFIG["id"]),
            headers={"Token": token}
        )

        if resp.status_code != 200:
            print("ERR: Failed to get latest data.")
            exit()

        with open(cache_file, "w") as f:
            data = resp.json()
            data["timestamp"] = time.time()

            f.write(json.dumps(data, indent=4))

            return data

    except Exception as e:
        if cache == None:
            # print("ERR: Unable to get data from cache or API")
            print(e)
            exit()

        return cache

# Convert a time like this: "2000-01-01T20:30:00+02:00"
# To a time like this: 1618805000
def apiTimeToUnixTime(apiTime: str):
    return int(datetime.datetime.strptime(apiTime, "%Y-%m-%dT%H:%M:%S%z").timestamp())

def unixTimeToNeatTime(unixTime: float):
    return datetime.datetime.utcfromtimestamp(unixTime).time().isoformat()[:-3]

# Get a (currentEvent, nextEvent) tuple
#   nextEvent is the next period for which there will be loadshedding
#   If we are currently loadshedding, currentEvent is the period it will last
#   If we aren't currently loadshedding, currentEvent is None
def getImmediateLoadsheddingEvents(data: dict, now: float):
    (currentEvent, nextEvent) = (None, None)

    # Events are sorted chronologically
    for event in data["events"]:

        start = apiTimeToUnixTime(event["start"])
        end = apiTimeToUnixTime(event["end"])
        stage = int(event["note"].split(" ")[1])

        neatEvent = {
            "start": start,
            "end": end,
            "stage": stage
        }

        if now < end and now >= start:
            # print(neatEvent)
            currentEvent = neatEvent

        if nextEvent == None and now < start:
            nextEvent = neatEvent
    
    return (currentEvent, nextEvent)

# Replace tags in the input string with the appropriate content
def formatOutput(inp: str, data: dict):
    (currEvent, nextEvent) = getImmediateLoadsheddingEvents(data, time.time())

    if (tag := "<areaName>") in inp:
        inp = inp.replace("<areaName>", CONFIG["name"])

    if (tag := "<areaRegion>") in inp:
        inp.replace(tag, CONFIG["region"])

    # If currently loadshedding show when it ends
    # Else show the next expected stage
    if (tag := "<when>") in inp:
        if nextEvent != None:
            if currEvent == None:
                inp = inp.replace(tag, "NEXT: " + unixTimeToNeatTime(nextEvent["start"]))
            else:
                inp = inp.replace(tag, "TILL: " + unixTimeToNeatTime(currEvent["end"]))
        else:
            inp.replace(tag, "NODATA")

    # Always show the next stage
    if (tag := "<next>") in inp:
        if nextEvent != None:
            inp = inp.replace(tag, unixTimeToNeatTime(nextEvent["start"]))
        else:
            inp = inp.replace(tag, "NODATA")
    
    return inp


if __name__ == "__main__":
    token = getToken()

    if len(sys.argv) > 1:
        data = getData(token)

        output = formatOutput(sys.argv[1], data)

        print(output)