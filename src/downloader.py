import requests
import os
import shutil
import tarfile

def download_file(url, file_path):
    print(f"Downloading {url} to {file_path}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
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
