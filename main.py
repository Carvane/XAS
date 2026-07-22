import os
import json

from dotenv import load_dotenv

from agent import Agent
from view import menu, menu_option, clear


def main():
    PATH_ACC = "data/acc.json"
    
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
                menuLatest(xas)
            case 2:
                menuBestRating(xas)
            case _:
                pass

def menuLatest(obj: Agent):
    pass

def menuBestRating(obj: Agent):
    pass



if __name__ == "__main__":
    main()