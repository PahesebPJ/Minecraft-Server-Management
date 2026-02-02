# Minecraft Server Management Tool

This tool helps you to automatically create and manage Minecraft servers using Docker.

For detailed documentation on how the project works, please see the [documentation here](./docs/en/README.md).

Para la documentación detallada en español, por favor vea la [documentación aquí](./docs/es/README.md).

## Requirements
- Python 3.6+
- Docker
- Java 17+ (for running mod loaders)

## Installation
```bash
pip install -r requirements.txt
```

## Usage

### Vanilla Server
```bash
python src/main.py --server-type vanilla --server-version <version> --xmx <max_memory> --xms <initial_memory>
```

### Modded Server (Forge/Fabric)
```bash
python src/main.py --server-type mods --server-version <version> --mod-loader <forge|fabric> --mod-config <path_to_mods.json> --xmx <max_memory> --xms <initial_memory>
```

### Arguments
- `--server-type`: The type of server to create. (choices: `vanilla`, `plugins`, `mods`)
- `--server-version`: The version of the Minecraft server to install.
- `--server-name`: Optional name for the server container and volume. Defaults to `mc-server-<version>`.
- `--xmx`: Maximum memory allocation for the server (e.g., 1024M, 2G). Default: 1024M.
- `--xms`: Initial memory allocation for the server (e.g., 1024M, 2G). Default: 1024M.

#### Modded Server Arguments
- `--mod-loader`: Mod loader type (required for `--server-type mods`). Choices: `forge`, `fabric`.
- `--mod-config`: Path to mod configuration JSON file (optional). See [Mod Configuration](#mod-configuration) below.
- `--curseforge-api-key`: CurseForge API key for downloading CurseForge mods. Can also be set via `CF_API_KEY` environment variable.

## Mod Configuration

For modded servers, you can specify mods to download automatically using a JSON configuration file.

### Configuration Format

```json
{
  "mod_loader": "fabric",
  "minecraft_version": "1.21.1",
  "mods": [
    {
      "platform": "modrinth",
      "slug": "fabric-api",
      "version": "latest"
    },
    {
      "platform": "curseforge",
      "slug": "jei",
      "version": "latest"
    }
  ]
}
```

### Fields
- `mod_loader`: Must match the `--mod-loader` argument (`forge` or `fabric`)
- `minecraft_version`: Minecraft version (should match `--server-version`)
- `mods`: Array of mod specifications
  - `platform`: `modrinth` or `curseforge`
  - `slug`: Mod identifier/slug from the platform
  - `version`: Version constraint (currently only `latest` is supported)

### CurseForge API Key

To download mods from CurseForge, you need a free API key:
1. Visit https://console.curseforge.com/
2. Create an account and generate an API key
3. Pass it via `--curseforge-api-key` or set the `CF_API_KEY` environment variable

**Note**: Modrinth does not require an API key.

## Examples

### Vanilla Server
```bash
python src/main.py --server-type vanilla --server-version 1.21.1 --xmx 2G --xms 2G
```

### Fabric Server with Mods
```bash
python src/main.py --server-type mods --server-version 1.21.1 --mod-loader fabric --mod-config mods-fabric-example.json --xmx 2G --xms 2G
```

This will:
1. Install Fabric server for Minecraft 1.21.1
2. Download mods specified in `mods-fabric-example.json` from Modrinth
3. Build a Docker image with the server and mods
4. Start a Docker container with 2GB RAM

### Forge Server with Mods
```bash
python src/main.py --server-type mods --server-version 1.20.1 --mod-loader forge --mod-config mods-forge-example.json --xmx 2G --xms 2G
```

### Modded Server without Mods Config
```bash
python src/main.py --server-type mods --server-version 1.21.1 --mod-loader fabric --xmx 2G
```

This will create a Fabric server with only Fabric API (no additional mods).

## Managing Your Server

After starting a server, you can manage it with these Docker commands:

```bash
# View server logs
docker logs <server-name>

# Follow logs in real-time
docker logs -f <server-name>

# Stop the server
docker stop <server-name>

# Start the server
docker start <server-name>

# Remove the server container
docker rm <server-name>

# Remove the server data volume (WARNING: deletes all server data)
docker volume rm <server-name>-data
```

## Notes
- The tool will ask for confirmation before performing major actions like downloading files or building/running Docker containers.
- Server data is persisted in Docker volumes, so it survives container restarts.
- For Fabric servers, Fabric API is automatically downloaded as it's required by most Fabric mods.
