import os
import subprocess
import requests
from typing import Optional
from downloader import download_file


def get_forge_installer_url(minecraft_version: str) -> Optional[str]:
    """
    Get the Forge installer download URL for a specific Minecraft version.
    
    Args:
        minecraft_version: Minecraft version (e.g., '1.20.1')
    
    Returns:
        Forge installer URL or None if not found
    """
    try:
        # Forge promotions API to get recommended version
        promotions_url = "https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json"
        response = requests.get(promotions_url)
        response.raise_for_status()
        promotions = response.json()
        
        # Try to find recommended version for this MC version
        promo_key = f"{minecraft_version}-recommended"
        latest_key = f"{minecraft_version}-latest"
        
        forge_version = promotions.get("promos", {}).get(promo_key)
        if not forge_version:
            forge_version = promotions.get("promos", {}).get(latest_key)
        
        if not forge_version:
            print(f"No Forge version found for Minecraft {minecraft_version}")
            return None
        
        # Construct download URL
        # Format: https://maven.minecraftforge.net/net/minecraftforge/forge/{mc_version}-{forge_version}/forge-{mc_version}-{forge_version}-installer.jar
        full_version = f"{minecraft_version}-{forge_version}"
        installer_url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{full_version}/forge-{full_version}-installer.jar"
        
        return installer_url
    
    except Exception as e:
        print(f"Error getting Forge installer URL: {e}")
        return None


def get_fabric_installer_url() -> str:
    """
    Get the latest Fabric installer download URL.
    
    Returns:
        Fabric installer URL
    """
    # Fabric installer is version-agnostic
    return "https://maven.fabricmc.net/net/fabricmc/fabric-installer/1.0.1/fabric-installer-1.0.1.jar"


def install_forge_server(minecraft_version: str, build_context_dir: str) -> Optional[str]:
    """
    Download and install Forge server.
    
    Args:
        minecraft_version: Minecraft version
        build_context_dir: Directory to install server files
    
    Returns:
        Path to server JAR or None if failed
    """
    print(f"Installing Forge server for Minecraft {minecraft_version}...")
    
    # Get installer URL
    installer_url = get_forge_installer_url(minecraft_version)
    if not installer_url:
        return None
    
    # Download installer
    installer_path = os.path.join(build_context_dir, "forge-installer.jar")
    if not download_file(installer_url, installer_path):
        print("Failed to download Forge installer")
        return None
    
    # Run installer
    print("Running Forge installer (this may take a few minutes)...")
    try:
        install_command = [
            "java",
            "-jar",
            installer_path,
            "--installServer"
        ]
        
        result = subprocess.run(
            install_command,
            cwd=build_context_dir,
            check=True,
            capture_output=True,
            text=True
        )
        
        print("Forge installer completed successfully")
        
        # Find the server JAR (Forge creates forge-{version}.jar or similar)
        for file in os.listdir(build_context_dir):
            if file.startswith("forge") and file.endswith(".jar") and "installer" not in file:
                server_jar_path = os.path.join(build_context_dir, file)
                # Rename to server.jar for consistency
                final_path = os.path.join(build_context_dir, "server.jar")
                os.rename(server_jar_path, final_path)
                print(f"Forge server JAR ready: server.jar")
                
                # Clean up installer
                if os.path.exists(installer_path):
                    os.remove(installer_path)
                
                return final_path
        
        # If no forge jar found, check for run.sh/run.bat which indicates newer Forge
        if os.path.exists(os.path.join(build_context_dir, "run.sh")) or \
           os.path.exists(os.path.join(build_context_dir, "run.bat")):
            print("Newer Forge version detected with run scripts")
            # For newer Forge, we need to use the run script
            # Create a marker file to indicate this
            marker_path = os.path.join(build_context_dir, "USE_RUN_SCRIPT")
            with open(marker_path, "w") as f:
                f.write("true")
            return marker_path
        
        print("Could not find Forge server JAR after installation")
        return None
    
    except subprocess.CalledProcessError as e:
        print(f"Forge installer failed: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return None
    except Exception as e:
        print(f"Error running Forge installer: {e}")
        return None


def install_fabric_server(minecraft_version: str, build_context_dir: str) -> Optional[str]:
    """
    Download and install Fabric server.
    
    Args:
        minecraft_version: Minecraft version
        build_context_dir: Directory to install server files
    
    Returns:
        Path to server launcher JAR or None if failed
    """
    print(f"Installing Fabric server for Minecraft {minecraft_version}...")
    
    # Get installer URL
    installer_url = get_fabric_installer_url()
    
    # Download installer
    installer_path = os.path.join(build_context_dir, "fabric-installer.jar")
    if not download_file(installer_url, installer_path):
        print("Failed to download Fabric installer")
        return None
    
    # Run installer
    print("Running Fabric installer...")
    try:
        install_command = [
            "java",
            "-jar",
            installer_path,
            "server",
            "-mcversion", minecraft_version,
            "-downloadMinecraft"
        ]
        
        result = subprocess.run(
            install_command,
            cwd=build_context_dir,
            check=True,
            capture_output=True,
            text=True
        )
        
        print("Fabric installer completed successfully")
        
        # Fabric creates fabric-server-launch.jar
        server_launcher = os.path.join(build_context_dir, "fabric-server-launch.jar")
        if os.path.exists(server_launcher):
            print(f"Fabric server launcher ready: fabric-server-launch.jar")
            
            # Clean up installer
            if os.path.exists(installer_path):
                os.remove(installer_path)
            
            # Download Fabric API (required for most Fabric mods)
            print("Downloading Fabric API...")
            mods_dir = os.path.join(build_context_dir, "mods")
            os.makedirs(mods_dir, exist_ok=True)
            
            try:
                from mod_platforms import ModrinthClient
                modrinth = ModrinthClient()
                fabric_api_path = modrinth.download_mod("fabric-api", minecraft_version, "fabric", mods_dir)
                if fabric_api_path:
                    print("Fabric API downloaded successfully")
                else:
                    print("Warning: Could not download Fabric API. Some mods may not work.")
            except Exception as e:
                print(f"Warning: Could not download Fabric API: {e}")
            
            return server_launcher
        else:
            print("Could not find fabric-server-launch.jar after installation")
            return None
    
    except subprocess.CalledProcessError as e:
        print(f"Fabric installer failed: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return None
    except Exception as e:
        print(f"Error running Fabric installer: {e}")
        return None


def get_mod_loader_type(build_context_dir: str) -> str:
    """
    Detect which mod loader is installed in the build context.
    
    Args:
        build_context_dir: Directory containing server files
    
    Returns:
        'fabric', 'forge', or 'unknown'
    """
    if os.path.exists(os.path.join(build_context_dir, "fabric-server-launch.jar")):
        return "fabric"
    elif os.path.exists(os.path.join(build_context_dir, "server.jar")):
        return "forge"
    elif os.path.exists(os.path.join(build_context_dir, "USE_RUN_SCRIPT")):
        return "forge"
    else:
        return "unknown"
