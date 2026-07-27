import os
import json

from dotenv import load_dotenv

from agent import Agent
from data import getAgents
from view import welcome, menu, menu_option, clear, logo

PATH_AGENT = 'data/agent.json'

def main():

    option = welcome()
    match option:
        case 0: #exit
            return
        case 1: #select
            optionMenu = agentOption(option)
            menuAgent(selected=optionMenu[0], nameAgent=optionMenu[1])
        case 2: #create
            menuAgent(agentOption(option))
        case 3: #delete
            menuAgent(agentOption(option))

def agentOption(selected: int, _clear: bool = True):
    clear(_clear)
    logo(20)
    match selected:
        case 1:
            agents = getAgents(PATH_AGENT)
            if agents:
                print("Choose an agent:\n")
                for nr, agentName in enumerate(agents, start=1):
                    print(f"[{nr}] {agentName}")
                while 1:
                    try:
                        option = int(input(": "))

                        if option >= 1 and option <= len(agents):
                            return (option, agentName)
                        else:
                            print(f"Please choose a number from 1 to {len(agents)}.")

                    except ValueError:
                        print("Please enter a correct number.")
            else:
                print("Create an agent first!")

def menuAgent(selected: int, nameAgent: str | None = None, _clear: bool = True):
    clear(_clear)
    logo(20)
    match selected:
        case 1:
            print(f"Selected agent: {nameAgent}\n")
            print("[1] Start")
            print("[2] Configuration")
            print("[3] Monitored Accounts")
            print("[4] Processed Posts IDs")
            print("[5] API Credentials")
            print("[0] Back to Main Menu")
        case 2:
            pass
        case 3:
            pass

"""
def main():
    PATH_ACC = "data/acc.json"
    LIST_NAME = "LIST_1"
    
    load_dotenv()
    
    xas = Agent(
        ConsumerKey=os.getenv("CONSUMER_KEY"),
        ConsumerKeySecret=os.getenv("CONSUMER_KEY_SECRET"),
        AccessToken=os.getenv("ACCESS_TOKEN"),
        AccessTokenSecret=os.getenv("ACCESS_TOKEN_SECRET"),
        OpenaiSecretKey=os.getenv("OPENAI_SECRET_KEY")
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
                #menuLatest(xas, PATH_ACC, LIST_NAME)
                x = xas.generateResponse("test ;d")
                print(x)
                input("")
            case 2:
                menuBestRating(xas, PATH_ACC, LIST_NAME)
            case _:
                pass 
"""

def menuLatest(obj: Agent, path: str, listName: str):
    with open(path) as file:
        lists = json.load(file)
    response = obj.getLatest(lists[listName])
    response = response["mess"]

    print(f"\n{response}\n")
    input("Press ENTER to continue")

def menuBestRating(obj: Agent):
    pass



if __name__ == "__main__":
    main()