import requests
import platform
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

def get_java_download_url(java_version, os_name):
    api_url = f"https://api.adoptium.net/v3/assets/feature_releases/{java_version}/ga"
    
    params = {
        "os": os_name,
        "architecture": "x64",
        "image_type": "jdk",
        "vendor": "eclipse",
        "heap_size": "normal",
    }

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        if data:
            return data[0]["binary"]["package"]["link"]
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error getting Java download URL: {e}")
        return None
    except (KeyError, IndexError):
        print("Could not find a download URL for the specified Java version.")
        return None

def download_and_extract_java(java_download_url, java_version):
    java_dir = f"jdk-{java_version}"
    os.makedirs(java_dir, exist_ok=True)
    
    file_name = java_download_url.split("/")[-1]
    file_path = os.path.join(java_dir, file_name)
    
    if download_file(java_download_url, file_path):
        print(f"Extracting {file_path}...")
        try:
            if file_path.endswith(".zip"):
                shutil.unpack_archive(file_path, java_dir)
            elif file_path.endswith(".tar.gz"):
                with tarfile.open(file_path, "r:gz") as tar:
                    tar.extractall(path=java_dir)
            os.remove(file_path)
            print("Extraction complete.")
            return java_dir
        except (shutil.ReadError, tarfile.TarError) as e:
            print(f"Error extracting Java: {e}")
            return None
    else:
        return None
