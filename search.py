import os
import sys
import json
import requests

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

if __name__ == "__main__":
    if len(sys.argv)>1 and sys.argv[1] in ["-h", "--help"]:
        print("This is a helper script to help you find valid areas for your config")
        print("Just run the script and enter a search term for your area.")
        print("\n\t $ python3 search.py\n")
        exit()

    token = getToken()

    print("Enter a search term for your area: ")
    area = input()

    resp = requests.get("https://developer.sepush.co.za/business/2.0/areas_search?text=" + area, headers={"Token": token})

    print("\033[92mSTATUS: " + str(resp.status_code) + "\033[0m")
    print(json.dumps(resp.json(), indent=4))