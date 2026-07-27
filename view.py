import os
import sys

def menu(_clear=1):
    clear(_clear)
    print("XAS generates a post based on accounts from LIST_1")
    print("Choose an option:\n")
    print("[1] Latest")
    print("[2] Highest-rated\n")
    print("[0] EXIT")

def welcome(_clear: bool = True):
    clear(_clear)
    logo(20)
    print("[1] Select an agent")
    print("[2] Create an agent")
    print("[3] Delete an agent")
    print("[0] Exit")

    while 1:
        try:
            option = int(input(": "))

            if option in (0,1,2,3):
                return option

        except ValueError:
            print("Please enter a correct number.")


def menu_option(value: int):
    pass

def logo(dashes: int = 0):
    dash = ""
    for x in range(dashes):
        dash += "-"
    print(f"[{dash} XAS {dash}]\n")

def clear(active: bool = True):
    if active:
        if sys.platform == "win32":
            os.system('cls')
        elif sys.platform == "linux":
            os.system('clear')