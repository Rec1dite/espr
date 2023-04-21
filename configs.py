# pylint: disable=C0103,C0116

"""Handles getting config information from local files"""

import os
import sys


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
