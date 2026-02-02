import requests
from tqdm import tqdm

def download_file(url, file_path):
    print(f"Downloading {url} to {file_path}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        with open(file_path, "wb") as f, tqdm(
            total=total_size, unit='iB', unit_scale=True, unit_divisor=1024,
        ) as bar:
            for chunk in response.iter_content(chunk_size=8192):
                size = f.write(chunk)
                bar.update(size)
        print("Download complete.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
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


def download_mods_from_config(config, output_dir, cf_api_key=None):
    """
    Download all mods specified in a mod configuration.
    
    Args:
        config: ModConfig object containing mod specifications
        output_dir: Directory to save downloaded mods
        cf_api_key: Optional CurseForge API key for CurseForge downloads
    
    Returns:
        List of successfully downloaded mod file paths
    """
    from mod_platforms import ModrinthClient, CurseForgeClient
    import os
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize clients
    modrinth_client = ModrinthClient()
    curseforge_client = None
    
    if cf_api_key:
        try:
            curseforge_client = CurseForgeClient(cf_api_key)
        except ValueError as e:
            print(f"Warning: {e}")
    
    downloaded_mods = []
    failed_mods = []
    
    print(f"\nDownloading {len(config.mods)} mod(s)...")
    
    for idx, mod in enumerate(config.mods, 1):
        print(f"\n[{idx}/{len(config.mods)}] Processing {mod.slug}...")
        
        try:
            if mod.platform == "modrinth":
                mod_path = modrinth_client.download_mod(
                    mod.slug,
                    config.minecraft_version,
                    config.mod_loader,
                    output_dir
                )
                if mod_path:
                    downloaded_mods.append(mod_path)
                else:
                    failed_mods.append(mod.slug)
            
            elif mod.platform == "curseforge":
                if not curseforge_client:
                    print(f"Skipping {mod.slug}: CurseForge API key not provided")
                    failed_mods.append(mod.slug)
                    continue
                
                mod_path = curseforge_client.download_mod(
                    mod.slug,
                    config.minecraft_version,
                    config.mod_loader,
                    output_dir
                )
                if mod_path:
                    downloaded_mods.append(mod_path)
                else:
                    failed_mods.append(mod.slug)
        
        except Exception as e:
            print(f"Error downloading {mod.slug}: {e}")
            failed_mods.append(mod.slug)
    
    # Summary
    print(f"\n{'='*50}")
    print(f"Download Summary:")
    print(f"  Successfully downloaded: {len(downloaded_mods)} mod(s)")
    if failed_mods:
        print(f"  Failed: {len(failed_mods)} mod(s)")
        print(f"  Failed mods: {', '.join(failed_mods)}")
    print(f"{'='*50}\n")
    
    return downloaded_mods
