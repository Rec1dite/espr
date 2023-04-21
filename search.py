"""A simple wrapper utility for the ESP API areas_search endpoint."""
# pylint: disable=C0103,C0116

import os
import sys
import json
import requests

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
