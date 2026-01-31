# Minecraft Server Management Tool

This tool helps you to automatically create a Minecraft server.

## Requirements
- Python 3.6+
- Java 8+

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python src/main.py --server-type <server_type> --server-version <server_version>
```

### Arguments
- `--server-type`: The type of server to create. (choices: `vanilla`, `plugins`, `mods`)
- `--server-version`: The version of the Minecraft server to install.

### Example
```bash
python src/main.py --server-type vanilla --server-version 1.18.2
```
