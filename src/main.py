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
        # Validate mod loader is specified
        if not args.mod_loader:
            print("Error: --mod-loader is required when --server-type is 'mods'")
            print("Please specify either 'forge' or 'fabric'")
            return
        
        if not confirm_action(f"Do you want to set up a {args.mod_loader.capitalize()} modded Minecraft server version {args.server_version} with Docker?"):
            return
        
        # 1. Prepare build context
        build_context_dir = os.path.join(os.getcwd(), "docker_build_context")
        os.makedirs(build_context_dir, exist_ok=True)
        
        try:
            # 2. Install mod loader
            from mod_loaders import install_forge_server, install_fabric_server, get_mod_loader_type
            
            print(f"\nInstalling {args.mod_loader.capitalize()} server...")
            if args.mod_loader == "forge":
                server_jar = install_forge_server(args.server_version, build_context_dir)
            else:  # fabric
                server_jar = install_fabric_server(args.server_version, build_context_dir)
            
            if not server_jar:
                print(f"Failed to install {args.mod_loader.capitalize()} server")
                return
            
            # 3. Download mods if config provided
            if args.mod_config:
                from mod_config import load_mod_config
                from downloader import download_mods_from_config
                
                print(f"\nLoading mod configuration from {args.mod_config}...")
                mod_config = load_mod_config(args.mod_config)
                
                if not mod_config:
                    print("Failed to load mod configuration")
                    return
                
                # Validate mod loader matches
                if mod_config.mod_loader != args.mod_loader:
                    print(f"Error: Mod config specifies '{mod_config.mod_loader}' but --mod-loader is '{args.mod_loader}'")
                    return
                
                # Validate Minecraft version matches
                if mod_config.minecraft_version != args.server_version:
                    print(f"Warning: Mod config specifies MC version '{mod_config.minecraft_version}' but --server-version is '{args.server_version}'")
                    if not confirm_action("Continue anyway?"):
                        return
                
                # Get CurseForge API key from args or environment
                cf_api_key = args.curseforge_api_key or os.environ.get("CF_API_KEY")
                
                # Download mods
                mods_dir = os.path.join(build_context_dir, "mods")
                downloaded_mods = download_mods_from_config(mod_config, mods_dir, cf_api_key)
                
                if not downloaded_mods and mod_config.mods:
                    print("Warning: No mods were downloaded successfully")
                    if not confirm_action("Continue with server setup anyway?"):
                        return
            else:
                print("\nNo mod configuration provided. Server will start with no additional mods.")
                print("(Fabric API is already included for Fabric servers)")
            
            # 4. Copy Dockerfile and entrypoint for modded servers
            dockerfile_src = os.path.join(os.getcwd(), "Dockerfile.modded")
            entrypoint_src = os.path.join(os.getcwd(), "entrypoint-modded.sh")
            
            # Check if modded versions exist, otherwise use vanilla versions
            if os.path.exists(dockerfile_src):
                shutil.copy(dockerfile_src, os.path.join(build_context_dir, "Dockerfile"))
            else:
                shutil.copy(os.path.join(os.getcwd(), "Dockerfile"), build_context_dir)
            
            if os.path.exists(entrypoint_src):
                shutil.copy(entrypoint_src, os.path.join(build_context_dir, "entrypoint.sh"))
            else:
                shutil.copy(os.path.join(os.getcwd(), "entrypoint.sh"), build_context_dir)
            
            # 5. Build Docker Image
            print(f"\nBuilding Docker image '{image_name}'...")
            build_command = ["docker", "build", "-t", image_name, build_context_dir]
            try:
                subprocess.run(build_command, check=True)
                print(f"Docker image '{image_name}' built successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Failed to build Docker image: {e}")
                return
            
            # 6. Run Docker Container
            print(f"\nRunning Docker container '{server_name}' from image '{image_name}'...")
            run_command = [
                "docker", "run", "-d",
                "--name", server_name,
                "-p", "25565:25565",  # Default Minecraft port
                "-e", "EULA=TRUE",  # Accept EULA inside the container
                "-e", f"XMX={args.xmx}",
                "-e", f"XMS={args.xms}",
                "-v", f"{server_data_volume}:/app",  # Mount volume for persistent data
                image_name
            ]
            try:
                subprocess.run(run_command, check=True)
                print(f"\n{'='*60}")
                print(f"Minecraft {args.mod_loader.capitalize()} server container '{server_name}' started successfully!")
                print(f"Server data is persisted in Docker volume: '{server_data_volume}'")
                print(f"Server is running on port 25565")
                print(f"\nUseful commands:")
                print(f"  View logs: docker logs {server_name}")
                print(f"  Stop server: docker stop {server_name}")
                print(f"  Start server: docker start {server_name}")
                print(f"{'='*60}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to run Docker container: {e}")
        
        finally:
            # 7. Clean up build context
            if os.path.exists(build_context_dir):
                shutil.rmtree(build_context_dir)
                print(f"\nCleaned up temporary build context: {build_context_dir}")

if __name__ == "__main__":
    main()

