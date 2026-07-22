import os
import json

from dotenv import load_dotenv

from agent import Agent
from view import menu, menu_option, clear


def main():
    PATH_ACC = "data/acc.json"
    LIST_NAME = "LIST_1"
    
    load_dotenv()
    
    xas = Agent(
        ConsumerKey=os.getenv("CONSUMER_KEY"),
        ConsumerKeySecret=os.getenv("CONSUMER_KEY_SECRET"),
        AccessToken=os.getenv("ACCESS_TOKEN"),
        AccessTokenSecret=os.getenv("ACCESS_TOKEN_SECRET")
    )
    while True:
        menu()
        try:
            optionMenu = int(input(": "))
        except:
            optionMenu = 1234567890

        match optionMenu:
            case 0:
                break
            case 1:
                menuLatest(xas, PATH_ACC, LIST_NAME)
            case 2:
                menuBestRating(xas, PATH_ACC, LIST_NAME)
            case _:
                pass

def menuLatest(obj: Agent, path: str, listName: str):
    with open(path) as file:
        lists = json.load(file)
    response = obj.getLatest(lists[listName])

    print(f"\n{response["mess"]}\n")
    input("Press ENTER to continue")

def menuBestRating(obj: Agent):
    pass



if __name__ == "__main__":
    main()