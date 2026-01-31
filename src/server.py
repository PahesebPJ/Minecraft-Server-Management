import os

def configure_server_properties(server_dir):
    properties_path = os.path.join(server_dir, "server.properties")
    try:
        with open(properties_path, "r") as f:
            for line in f:
                if not line.startswith("#"):
                    print(line.strip())
    except FileNotFoundError:
        print("server.properties not found. The server may not have been run yet.")
