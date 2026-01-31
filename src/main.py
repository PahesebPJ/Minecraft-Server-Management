import argparse
import platform
import subprocess
import os
import requests
from downloader import download_file
from server import run_server, configure_server_properties, generate_start_script

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
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Java is not installed. Please install Java and try again.")
        return False

def get_vanilla_download_url(version):
    try:
        response = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json")
        response.raise_for_status()
        manifest = response.json()
        for v in manifest["versions"]:
            if v["id"] == version:
                version_url = v["url"]
                version_data = requests.get(version_url).json()
                return version_data["downloads"]["server"]["url"]
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error getting download URL: {e}")
        return None

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

def main():
    parser = argparse.ArgumentParser(description="Minecraft Server Management Tool")
    parser.add_argument("--server-type", choices=["vanilla", "plugins", "mods"], required=True, help="Type of server to create.")
    parser.add_argument("--server-version", required=True, help="Version of the Minecraft server to install.")
    
    args = parser.parse_args()
    
    operating_system = get_operating_system()
    
    print("Minecraft Server Management Tool")
    print(f"Operating System: {operating_system}")
    print(f"Server Type: {args.server_type}")
    print(f"Server Version: {args.server_version}")
    
    if not check_java():
        return

    server_dir = f"mc-server-{args.server_version}"
    if args.server_type == "vanilla":
        download_url = get_vanilla_download_url(args.server_version)
        if download_url:
            os.makedirs(server_dir, exist_ok=True)
            server_jar_path = os.path.join(server_dir, "server.jar")
            if download_file(download_url, server_jar_path):
                run_server(server_dir)
                accept_eula(server_dir)
                configure_server_properties(server_dir)
                generate_start_script(server_dir, operating_system)

    elif args.server_type == "plugins":
        print("Plugin server download not implemented yet.")
    elif args.server_type == "mods":
        print("Modded server download not implemented yet.")

if __name__ == "__main__":
    main()
