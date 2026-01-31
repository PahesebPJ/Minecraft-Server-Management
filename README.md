# Minecraft Server Management Tool

This tool helps you to automatically create a Minecraft server.

## Requirements
- Python 3.6+
- Java 17 or higher (Optional)

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python src/main.py --server-type <server_type> --server-version <server_version> --xmx <xmx> --xms <xms>
```

### Arguments
- `--server-type`: The type of server to create. (choices: `vanilla`, `plugins`, `mods`)
- `--server-version`: The version of the Minecraft server to install.
- `--xmx`: Maximum memory allocation for the server (e.g., 1024M, 2G). Default: 1024M.
- `--xms`: Initial memory allocation for the server (e.g., 1024M, 2G). Default: 1024M.

### Java
If Java is not installed, the tool will prompt you to download it. You will be asked to enter the desired Java version (e.g., 17, 18). The tool will then download and extract the JDK from [Adoptium](https://adoptium.net/).

### Notes
- The tool will ask for confirmation before performing major actions like downloading files or running the server.
