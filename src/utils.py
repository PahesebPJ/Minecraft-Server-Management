import platform
import os

def confirm_action(message):
    while True:
        choice = input(f"{message} (y/n): ").lower()
        if choice in ["y", "yes"]:
            return True
        elif choice in ["n", "no"]:
            return False
        else:
            print("Invalid choice. Please enter 'y' or 'n'.")

def get_operating_system():
    os_name = platform.system().lower()
    if "windows" in os_name:
        return "windows"
    elif "linux" in os_name:
        return "linux"
    else:
        return os_name
