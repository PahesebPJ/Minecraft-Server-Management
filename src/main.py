import os
import shutil
import subprocess
from cli import parse_args
from downloader import download_file, get_vanilla_download_url
from utils import confirm_action, get_operating_system

def main():
    args = parse_args()
    
    operating_system = get_operating_system()
    
    print("Minecraft Server Management Tool")
    print(f"Operating System: {operating_system}")
    print(f"Server Type: {args.server_type}")
    print(f"Server Version: {args.server_version}")
    
    server_name = args.server_name if args.server_name else f"mc-server-{args.server_version}"
    server_data_volume = f"{server_name}-data"
    image_name = f"minecraft-{args.server_type}-server:{args.server_version}"

    if args.server_type == "vanilla":
        if not confirm_action(f"Do you want to download the vanilla Minecraft server version {args.server_version} and set it up with Docker?"):
            return

        # 1. Prepare build context
        build_context_dir = os.path.join(os.getcwd(), "docker_build_context")
        os.makedirs(build_context_dir, exist_ok=True)

        try:
            # 2. Download server JAR
            download_url = get_vanilla_download_url(args.server_version)
            if not download_url:
                print("Failed to get vanilla server download URL.")
                return

            server_jar_path_in_context = os.path.join(build_context_dir, "server.jar")
            if not download_file(download_url, server_jar_path_in_context):
                print("Failed to download server JAR.")
                return

            # 3. Copy Dockerfile and entrypoint.sh to build context
            shutil.copy(os.path.join(os.getcwd(), "Dockerfile"), build_context_dir)
            shutil.copy(os.path.join(os.getcwd(), "entrypoint.sh"), build_context_dir)

            # 4. Build Docker Image
            print(f"Building Docker image '{image_name}'...")
            build_command = ["docker", "build", "-t", image_name, build_context_dir]
            try:
                subprocess.run(build_command, check=True)
                print(f"Docker image '{image_name}' built successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Failed to build Docker image: {e}")
                return

            # 5. Run Docker Container
            print(f"Running Docker container '{server_name}' from image '{image_name}'...")
            run_command = [
                "docker", "run", "-d",
                "--name", server_name,
                "-p", "25565:25565", # Default Minecraft port
                "-e", "EULA=TRUE", # Accept EULA inside the container
                "-e", f"XMX={args.xmx}",
                "-e", f"XMS={args.xms}",
                "-v", f"{server_data_volume}:/app", # Mount volume for persistent data
                image_name
            ]
            try:
                subprocess.run(run_command, check=True)
                print(f"Minecraft server container '{server_name}' started successfully!")
                print(f"Server data is persisted in Docker volume: '{server_data_volume}'")
            except subprocess.CalledProcessError as e:
                print(f"Failed to run Docker container: {e}")

        finally:
            # 6. Clean up build context
            if os.path.exists(build_context_dir):
                shutil.rmtree(build_context_dir)
                print(f"Cleaned up temporary build context: {build_context_dir}")
    elif args.server_type == "plugins":
        print("Plugin server setup with Docker not implemented yet.")
    elif args.server_type == "mods":
        print("Modded server setup with Docker not implemented yet.")

if __name__ == "__main__":
    main()

