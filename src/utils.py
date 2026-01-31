import platform
import subprocess
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

def check_java():
    try:
        subprocess.run(["java", "-version"], check=True, capture_output=True, text=True)
        print("Java is installed.")
        return "installed"
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Java is not installed.")
        while True:
            choice = input("Do you want to download Java? (y/n): ").lower()
            if choice in ["y", "yes"]:
                return "download"
            elif choice in ["n", "no"]:
                return "abort"
            else:
                print("Invalid choice. Please enter 'y' or 'n'.")

def accept_eula(server_dir):
    eula_path = os.path.join(server_dir, "eula.txt")
    try:
        with open(eula_path, "r") as f:
            content = f.read()
        with open(eula_path, "w") as f:
            f.write(content.replace("eula=false", "eula=true"))
        print("EULA accepted.")
    except FileNotFoundError:
        print("eula.txt not found. The server may not have been run yet.")