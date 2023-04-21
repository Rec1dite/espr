#!/bin/python3
# pylint: disable=C0103,C0116

"""A simple wrapper utility for the ESP API areas_search endpoint."""

import sys
import json
import requests
from configs import getToken

if __name__ == "__main__":
    if len(sys.argv)>1 and sys.argv[1] in ["-h", "--help"]:
        print("This is a helper script to help you find valid areas for your config")
        print("Just run the script and enter a search term for your area.")
        print("\n\t $ python3 search.py\n")
        sys.exit()

    token = getToken()

    print("Enter a search term for your area: ")
    area = input()

    resp = requests.get(
        f"https://developer.sepush.co.za/business/2.0/areas_search?text={area}",
        headers={"Token": token},
        timeout=10
    )

    print("\033[92mSTATUS: " + str(resp.status_code) + "\033[0m")
    print(json.dumps(resp.json(), indent=4))
