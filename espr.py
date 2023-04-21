#!/bin/python3
# pylint: disable=C0103,C0116

"""A simple polybar module to remind you when loadshedding is scheduled."""

import os
import sys
import time
import datetime
import json
import requests

CONFIG = {
    "id": "region-x-area",
    "name": "YOURAREA (x)",
    "region": "YourRegion",
    "refresh": 30, # How often to refresh the data in minutes
}

# Get the ESP API token from the token file
def getToken() -> (str | None):
    token_file = os.path.dirname(os.path.realpath(__file__)) + os.sep + "token"

    if not os.path.exists(token_file):
        print("ERR: No token file found.")
        print(
            "Please create a file called 'token' within the same directory" +
            "as this script and paste your ESP API token in it."
        )
        sys.exit()

    with open(token_file, "r", encoding="utf-8") as f:
        tok = f.read()
        if tok == "":
            print("ERR: Token file is empty.")
            sys.exit()

        return tok if tok != "" else None


# Cache + Return the latest loadshedding data for the area
# Data cache is refreshed every CONFIG["refresh"] minutes
def getData(tok):
    cache_file = os.path.dirname(os.path.realpath(__file__)) + os.sep + "cache.json"
    cache = None

    # Check if we have a cached version of the data
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            try:
                raw = f.read()

                if raw != "":
                    cache = json.loads(raw)
                    if cache["timestamp"] + (CONFIG["refresh"] * 60) > time.time():
                        return cache

            except ValueError:
                pass # Ignore errors, we'll just try get the data again

    # Get the latest data
    try:
        resp = requests.get(
            f"https://developer.sepush.co.za/business/2.0/area?id={CONFIG['id']}",
            headers={"Token": tok},
            timeout=10
        )

        if resp.status_code != 200:
            print("ERR: Failed to get latest data. Code ", resp.status_code)
            sys.exit()

        with open(cache_file, "w", encoding="utf-8") as f:
            dat = resp.json()
            dat["timestamp"] = time.time()

            f.write(json.dumps(dat, indent=4))

            return dat

    except ValueError as e:
        if cache is None:
            # print("ERR: Unable to get data from cache or API")
            print(e)
            sys.exit()

        return cache

# Convert a time like this: "2000-01-01T20:30:00+02:00"
# To a time like this: 1618805000
def apiTimeToUnixTime(apiTime: str):
    return int(datetime.datetime.strptime(apiTime, "%Y-%m-%dT%H:%M:%S%z").timestamp())

def unixTimeToNeatTime(unixTime: float):
    return datetime.datetime.fromtimestamp(unixTime).strftime("%H:%M")

# Get a (currentEvent, nextEvent) tuple
#   nextEvent is the next period for which there will be loadshedding
#   If we are currently loadshedding, currentEvent is the period it will last
#   If we aren't currently loadshedding, currentEvent is None
def getImmediateLoadsheddingEvents(dat: dict, now: float):
    (currentEvent, nextEvent) = (None, None)

    # Events are sorted chronologically
    for event in dat["events"]:

        start = apiTimeToUnixTime(event["start"])
        end = apiTimeToUnixTime(event["end"])
        stage = int(event["note"].split(" ")[1])

        neatEvent = {
            "start": start,
            "end": end,
            "stage": stage
        }

        if start <= now < end:
            # print(neatEvent)
            currentEvent = neatEvent

        if nextEvent is None and now < start:
            nextEvent = neatEvent

    return (currentEvent, nextEvent)

# Replace tags in the input string with the appropriate content
def formatOutput(inp: str, dat: dict):
    (currEvent, nextEvent) = getImmediateLoadsheddingEvents(dat, time.time())

    if (tag := "<areaName>") in inp:
        inp = inp.replace("<areaName>", CONFIG["name"])

    if (tag := "<areaRegion>") in inp:
        inp.replace(tag, CONFIG["region"])

    # If currently loadshedding show when it ends
    # Else show the next expected stage
    if (tag := "<when>") in inp:
        if nextEvent is not None:
            if currEvent is None:
                inp = inp.replace(tag, "NEXT: " + unixTimeToNeatTime(nextEvent["start"]))
            else:
                inp = inp.replace(tag, "TILL: " + unixTimeToNeatTime(currEvent["end"]))
        else:
            inp.replace(tag, "NODATA")

    # Always show the next stage
    if (tag := "<next>") in inp:
        if nextEvent is not None:
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
