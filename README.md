# Minecraft Server Management Tool

This tool helps you to automatically create and manage a Minecraft server using Docker.

For detailed documentation on how the project works, please see the [documentation here](./docs/ENG/README.md).

Para la documentación detallada en español, por favor vea la [documentación aquí](./docs/SPA/README.md).

## Requirements
- Python 3.6+
- Docker

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python src/main.py --server-type <server_type> --server-version <server_version> --xmx <max_memory> --xms <initial_memory>
```

### Arguments
- `--server-type`: The type of server to create. (choices: `vanilla`, `plugins`, `mods`)
- `--server-version`: The version of the Minecraft server to install.
- `--server-name`: Optional name for the server container and volume. Defaults to `mc-server-<version>`.
- `--xmx`: Maximum memory allocation for the server (e.g., 1024M, 2G). Default: 1024M.
- `--xms`: Initial memory allocation for the server (e.g., 1024M, 2G). Default: 1024M.

### Notes
- The tool will ask for confirmation before performing major actions like downloading files or building/running Docker containers.

### Example
```bash
python src/main.py --server-type vanilla --server-version 1.21.11 --xmx 2G --xms 2G
```

This command will:
1.  Download the Minecraft 1.21.11 vanilla server JAR.
2.  Build a Docker image with the server.
3.  Start a Docker container for the server, mapping port 25565, allocating 2GB of RAM, and persisting server data in a Docker volume.
