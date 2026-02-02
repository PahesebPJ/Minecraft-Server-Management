import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Minecraft Server Management Tool")
    parser.add_argument("--server-type", choices=["vanilla", "plugins", "mods", "bedrock"], required=True, help="Type of server to create.")
    parser.add_argument("--server-version", required=True, help="Version of the Minecraft server to install.")
    parser.add_argument("--server-name", help="Optional name for the server container and volume.")
    parser.add_argument("--xmx", default="1024M", help="Maximum memory allocation for the server (e.g., 1024M, 2G).")
    parser.add_argument("--xms", default="1024M", help="Initial memory allocation for the server (e.g., 1024M, 2G).")
    
    # Modded server arguments
    parser.add_argument("--mod-loader", choices=["forge", "fabric"], help="Mod loader type (required for --server-type mods).")
    parser.add_argument("--mod-config", help="Path to mod configuration JSON file (optional for --server-type mods).")
    parser.add_argument("--curseforge-api-key", help="CurseForge API key for downloading CurseForge mods.")
    
    return parser.parse_args()
