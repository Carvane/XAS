import os
import sys

def menu(_clear=1):
    if _clear:
        clear()
    print("XAS generates a post based on accounts from LIST_1")
    print("Choose an option:\n")
    print("[1] Latest")
    print("[2] Highest-rated\n")
    print("[0] EXIT")


def menu_option(value: int):
    pass

def clear():
    if sys.platform == "win32":
        os.system('cls')
    elif sys.platform == "linux":
        os.system('clear')