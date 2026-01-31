import argparse
import platform
import subprocess
import os
import requests
from downloader import download_file, get_java_download_url, download_and_extract_java
from server import run_server, configure_server_properties, generate_start_script, find_java_executable

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
    parser.add_argument("--xmx", default="1024M", help="Maximum memory allocation for the server (e.g., 1024M, 2G).")
    parser.add_argument("--xms", default="1024M", help="Initial memory allocation for the server (e.g., 1024M, 2G).")
    
    args = parser.parse_args()
    
    operating_system = get_operating_system()
    
    print("Minecraft Server Management Tool")
    print(f"Operating System: {operating_system}")
    print(f"Server Type: {args.server_type}")
    print(f"Server Version: {args.server_version}")
    
    java_executable = "java"
    java_status = check_java()
    if java_status == "abort":
        return
    elif java_status == "download":
        java_version = input("Enter the Java version to download (e.g., 17, 18): ")
        java_download_url = get_java_download_url(java_version, operating_system)
        if java_download_url:
            java_dir = download_and_extract_java(java_download_url, java_version)
            if java_dir:
                java_executable = find_java_executable(java_dir)
                if not java_executable:
                    print("Could not find java executable in the downloaded JDK.")
                    return
        else:
            print("Could not find a download for the specified Java version.")
            return

    server_dir = f"mc-server-{args.server_version}"
    if args.server_type == "vanilla":
        download_url = get_vanilla_download_url(args.server_version)
        if download_url:
            os.makedirs(server_dir, exist_ok=True)
            server_jar_path = os.path.join(server_dir, "server.jar")
            if download_file(download_url, server_jar_path):
                run_server(server_dir, java_executable=java_executable, xmx=args.xmx, xms=args.xms)
                accept_eula(server_dir)
                configure_server_properties(server_dir)
                generate_start_script(server_dir, operating_system, java_executable=java_executable, xmx=args.xmx, xms=args.xms)

    elif args.server_type == "plugins":
        print("Plugin server download not implemented yet.")
    elif args.server_type == "mods":
        print("Modded server download not implemented yet.")

if __name__ == "__main__":
    main()
