import requests
from typing import Optional, Dict, Any
from tqdm import tqdm
import os

class ModrinthClient:
    """Client for interacting with the Modrinth API to download Minecraft mods."""
    
    BASE_URL = "https://api.modrinth.com/v2"
    USER_AGENT = "Minecraft-Server-Management/0.0.1"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENT})
    
    def search_mod(self, slug: str, game_version: str, mod_loader: str) -> Optional[Dict[str, Any]]:
        """
        Search for a mod by slug and filter by game version and mod loader.
        
        Args:
            slug: The mod's slug (e.g., 'sodium', 'fabric-api')
            game_version: Minecraft version (e.g., '1.21.1')
            mod_loader: Mod loader type ('fabric' or 'forge')
        
        Returns:
            Dict containing project info and matching version, or None if not found
        """
        try:
            # Get project details
            project_url = f"{self.BASE_URL}/project/{slug}"
            project_response = self.session.get(project_url)
            project_response.raise_for_status()
            project_data = project_response.json()
            
            # Get project versions
            versions_url = f"{self.BASE_URL}/project/{slug}/version"
            params = {
                "game_versions": f'["{game_version}"]',
                "loaders": f'["{mod_loader}"]'
            }
            versions_response = self.session.get(versions_url, params=params)
            versions_response.raise_for_status()
            versions_data = versions_response.json()
            
            if not versions_data:
                print(f"No compatible version found for {slug} (MC {game_version}, {mod_loader})")
                return None
            
            # Get the latest compatible version
            latest_version = versions_data[0]
            
            return {
                "project": project_data,
                "version": latest_version
            }
        
        except requests.exceptions.RequestException as e:
            print(f"Error searching for mod '{slug}' on Modrinth: {e}")
            return None
    
    def get_mod_download_url(self, version_data: Dict[str, Any]) -> Optional[str]:
        """
        Extract the download URL from version data.
        
        Args:
            version_data: Version data from the API
        
        Returns:
            Download URL string or None
        """
        try:
            files = version_data.get("files", [])
            if not files:
                return None
            
            # Get the primary file
            primary_file = next((f for f in files if f.get("primary", False)), files[0])
            return primary_file.get("url")
        
        except Exception as e:
            print(f"Error extracting download URL: {e}")
            return None
    
    def download_mod(self, slug: str, game_version: str, mod_loader: str, output_dir: str) -> Optional[str]:
        """
        Download a mod from Modrinth.
        
        Args:
            slug: The mod's slug
            game_version: Minecraft version
            mod_loader: Mod loader type
            output_dir: Directory to save the mod file
        
        Returns:
            Path to downloaded file or None if failed
        """
        print(f"Searching for '{slug}' on Modrinth...")
        mod_data = self.search_mod(slug, game_version, mod_loader)
        
        if not mod_data:
            return None
        
        download_url = self.get_mod_download_url(mod_data["version"])
        if not download_url:
            print(f"No download URL found for {slug}")
            return None
        
        # Get filename from version data
        files = mod_data["version"].get("files", [])
        primary_file = next((f for f in files if f.get("primary", False)), files[0])
        filename = primary_file.get("filename", f"{slug}.jar")
        
        output_path = os.path.join(output_dir, filename)
        
        print(f"Downloading {filename} from Modrinth...")
        try:
            response = self.session.get(download_url, stream=True)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            
            with open(output_path, "wb") as f, tqdm(
                total=total_size, unit='iB', unit_scale=True, unit_divisor=1024,
            ) as bar:
                for chunk in response.iter_content(chunk_size=8192):
                    size = f.write(chunk)
                    bar.update(size)
            
            print(f"Successfully downloaded {filename}")
            return output_path
        
        except requests.exceptions.RequestException as e:
            print(f"Error downloading mod: {e}")
            return None


class CurseForgeClient:
    """Client for interacting with the CurseForge API to download Minecraft mods."""
    
    BASE_URL = "https://api.curseforge.com/v1"
    USER_AGENT = "Minecraft-Server-Management/1.0.0"
    MINECRAFT_GAME_ID = 432  # CurseForge game ID for Minecraft
    
    def __init__(self, api_key: str):
        """
        Initialize CurseForge client with API key.
        
        Args:
            api_key: CurseForge API key from https://console.curseforge.com/
        """
        if not api_key:
            raise ValueError("CurseForge API key is required")
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.USER_AGENT,
            "x-api-key": api_key
        })
    
    def search_mod(self, slug: str, game_version: str, mod_loader: str) -> Optional[Dict[str, Any]]:
        """
        Search for a mod by slug and filter by game version and mod loader.
        
        Args:
            slug: The mod's slug or name
            game_version: Minecraft version (e.g., '1.20.1')
            mod_loader: Mod loader type ('fabric' or 'forge')
        
        Returns:
            Dict containing mod info and matching file, or None if not found
        """
        try:
            # Search for the mod
            search_url = f"{self.BASE_URL}/mods/search"
            params = {
                "gameId": self.MINECRAFT_GAME_ID,
                "slug": slug,
                "classId": 6  # Mods class
            }
            
            search_response = self.session.get(search_url, params=params)
            search_response.raise_for_status()
            search_data = search_response.json()
            
            if not search_data.get("data"):
                print(f"Mod '{slug}' not found on CurseForge")
                return None
            
            mod = search_data["data"][0]
            mod_id = mod["id"]
            
            # Get mod files
            files_url = f"{self.BASE_URL}/mods/{mod_id}/files"
            files_response = self.session.get(files_url)
            files_response.raise_for_status()
            files_data = files_response.json()
            
            # Filter files by game version and mod loader
            compatible_files = []
            for file in files_data.get("data", []):
                game_versions = file.get("gameVersions", [])
                
                # Check if file matches game version and mod loader
                has_version = game_version in game_versions
                has_loader = mod_loader.lower() in [v.lower() for v in game_versions]
                
                if has_version and has_loader:
                    compatible_files.append(file)
            
            if not compatible_files:
                print(f"No compatible files found for {slug} (MC {game_version}, {mod_loader})")
                return None
            
            # Sort by file date (newest first)
            compatible_files.sort(key=lambda x: x.get("fileDate", ""), reverse=True)
            latest_file = compatible_files[0]
            
            return {
                "mod": mod,
                "file": latest_file
            }
        
        except requests.exceptions.RequestException as e:
            print(f"Error searching for mod '{slug}' on CurseForge: {e}")
            return None
    
    def get_mod_file_url(self, mod_id: int, file_id: int) -> Optional[str]:
        """
        Get download URL for a specific mod file.
        
        Args:
            mod_id: CurseForge mod ID
            file_id: CurseForge file ID
        
        Returns:
            Download URL or None
        """
        try:
            url = f"{self.BASE_URL}/mods/{mod_id}/files/{file_id}/download-url"
            response = self.session.get(url)
            response.raise_for_status()
            return response.json().get("data")
        
        except requests.exceptions.RequestException as e:
            print(f"Error getting download URL: {e}")
            return None
    
    def download_mod(self, slug: str, game_version: str, mod_loader: str, output_dir: str) -> Optional[str]:
        """
        Download a mod from CurseForge.
        
        Args:
            slug: The mod's slug
            game_version: Minecraft version
            mod_loader: Mod loader type
            output_dir: Directory to save the mod file
        
        Returns:
            Path to downloaded file or None if failed
        """
        print(f"Searching for '{slug}' on CurseForge...")
        mod_data = self.search_mod(slug, game_version, mod_loader)
        
        if not mod_data:
            return None
        
        mod_id = mod_data["mod"]["id"]
        file_id = mod_data["file"]["id"]
        filename = mod_data["file"]["fileName"]
        
        download_url = self.get_mod_file_url(mod_id, file_id)
        if not download_url:
            print(f"No download URL found for {slug}")
            return None
        
        output_path = os.path.join(output_dir, filename)
        
        print(f"Downloading {filename} from CurseForge...")
        try:
            response = self.session.get(download_url, stream=True)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            
            with open(output_path, "wb") as f, tqdm(
                total=total_size, unit='iB', unit_scale=True, unit_divisor=1024,
            ) as bar:
                for chunk in response.iter_content(chunk_size=8192):
                    size = f.write(chunk)
                    bar.update(size)
            
            print(f"Successfully downloaded {filename}")
            return output_path
        
        except requests.exceptions.RequestException as e:
            print(f"Error downloading mod: {e}")
            return None
