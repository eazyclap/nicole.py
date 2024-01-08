from time import sleep
from os import system

# TODO Quite useless innit? Linux server restarts the service automatically, remove this code.

# Activate this, set false for testing
# TODO ACTIVATE
IN_FUNCTION = False

if IN_FUNCTION:
    sleep(7)
    system("python main.py")
