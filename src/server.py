import subprocess
import os

def run_server(server_dir, server_jar="server.jar"):
    java_command = f"java -Xmx1024M -Xms1024M -jar {server_jar} nogui"
    
    # Change the working directory to the server directory
    original_cwd = os.getcwd()
    os.chdir(server_dir)
    
    try:
        print(f"Running server with command: {java_command}")
        # We expect this to fail because the eula is not accepted yet
        subprocess.run(java_command.split(), check=False)
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

def generate_start_script(server_dir, os_name):
    if os_name == "windows":
        script_path = os.path.join(server_dir, "start.bat")
        script_content = "java -Xmx1024M -Xms1024M -jar server.jar nogui\npause"
    elif os_name == "linux":
        script_path = os.path.join(server_dir, "start.sh")
        script_content = "#!/bin/bash\njava -Xmx1024M -Xms1024M -jar server.jar nogui"
    else:
        print(f"Unsupported OS: {os_name}")
        return

    try:
        with open(script_path, "w") as f:
            f.write(script_content)
        print(f"Generated start script: {script_path}")
    except IOError as e:
        print(f"Error generating start script: {e}")
