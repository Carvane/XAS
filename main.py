import os

from dotenv import load_dotenv

from agent import Agent
from view import menu, menu_option, clear

def main():
    menu()
    xas = Agent(
        ConsumerKey=os.getenv("CONSUMER_KEY"),
        ConsumerKeySecret=os.getenv("CONSUMER_KEY_SECRET"),
        AccessToken=os.getenv("ACCESS_TOKEN"),
        AccessTokenSecret=os.getenv("ACCESS_TOKEN_SECRET")
    )
    """ x = xas.getLatest(["solana", "pumpfun"])
    print(x) """
    #print(xas.postCreate("test"))



if __name__ == "__main__":
    load_dotenv()
    main()