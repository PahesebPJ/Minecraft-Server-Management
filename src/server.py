import subprocess
import os

def find_java_executable(java_dir):
    for root, dirs, files in os.walk(java_dir):
        for file in files:
            if file == "java" or file == "java.exe":
                return os.path.join(root, file)
    return None

def run_server(server_dir, server_jar="server.jar", java_executable="java", xmx="1024M", xms="1024M"):
    java_command = f'"{java_executable}" -Xmx{xmx} -Xms{xms} -jar {server_jar} nogui'
    
    # Change the working directory to the server directory
    original_cwd = os.getcwd()
    os.chdir(server_dir)
    
    try:
        print(f"Running server with command: {java_command}")
        # We expect this to fail because the eula is not accepted yet
        subprocess.run(java_command, shell=True, check=False)
    finally:
        # Change back to the original working directory
        os.chdir(original_cwd)

def configure_server_properties(server_dir):
    properties_path = os.path.join(server_dir, "server.properties")
    try:
        with open(properties_path, "r") as f:
            for line in f:
                if not line.startswith("#"):
                    print(line.strip())
    except FileNotFoundError:
        print("server.properties not found. The server may not have been run yet.")

def generate_start_script(server_dir, os_name, java_executable="java", xmx="1024M", xms="1024M"):
    if os_name == "windows":
        script_path = os.path.join(server_dir, "start.bat")
        script_content = f'"{java_executable}" -Xmx{xmx} -Xms{xms} -jar server.jar nogui\npause'
    elif os_name == "linux":
        script_path = os.path.join(server_dir, "start.sh")
        script_content = f'#!/bin/bash\n"{java_executable}" -Xmx{xmx} -Xms{xms} -jar server.jar nogui'
    else:
        print(f"Unsupported OS: {os_name}")
        return

    try:
        with open(script_path, "w") as f:
            f.write(script_content)
        print(f"Generated start script: {script_path}")
    except IOError as e:
        print(f"Error generating start script: {e}")
