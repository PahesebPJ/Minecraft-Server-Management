# Project Documentation

## Project Overview

This tool provides a simple command-line interface (CLI) to automate the creation and management of a Minecraft server. It leverages Docker to create a portable, consistent, and isolated environment for the server, removing the need for users to have Java installed on their host machines.

The primary goal is to simplify the setup process to a single command, allowing users to specify the server version and memory allocation, and have a server up and running in minutes.

## How it Works

The tool's workflow is orchestrated by the main Python script (`src/main.py`) and revolves around Docker.

1.  **User Input**: The script first parses user-provided arguments from the command line, such as server type, version, and memory settings (`--xmx`, `--xms`).

2.  **Download**: It downloads the official Minecraft server JAR file corresponding to the user's selected version.

3.  **Docker Build Context**: A temporary directory (`docker_build_context`) is created. The script copies the following into this directory:
    *   The downloaded `server.jar`.
    *   The project's `Dockerfile`.
    *   The `entrypoint.sh` script.

4.  **Docker Image Build**: The script then invokes `docker build`. Docker uses the `Dockerfile` in the build context to create a new Docker image. The `Dockerfile` specifies the base Java image, copies the `server.jar` and `entrypoint.sh` into the image, and sets the entrypoint.

5.  **Docker Container Run**: Once the image is built, the script runs a new Docker container from it using `docker run`. It passes several important parameters:
    *   **Environment Variables**: It sets `EULA=TRUE`, `XMX`, and `XMS` as environment variables inside the container.
    *   **Port Mapping**: It maps port `25565` on the host to port `25565` in the container, allowing users to connect to the Minecraft server.
    *   **Volume Mounting**: It creates and mounts a Docker volume. This is crucial for persisting the server data (world files, player data, etc.) even if the container is removed.

6.  **Container Initialization**: When the container starts, it automatically executes the `entrypoint.sh` script, which:
    *   Accepts the EULA on behalf of the user.
    *   Launches the Minecraft server using the specified memory settings.

7.  **Cleanup**: Finally, the main Python script removes the temporary `docker_build_context` directory, leaving the system clean.

## Project Structure

-   `Dockerfile`: The recipe for building the Minecraft server Docker image. It specifies the base Java image, copies necessary files, and sets the container's entrypoint.
-   `entrypoint.sh`: A shell script that runs when the Docker container starts. It handles EULA acceptance and launches the Java process for the Minecraft server.
-   `requirements.txt`: Lists the Python dependencies required for the project.
-   `.gitignore`: Specifies files and directories that should be ignored by Git (e.g., `venv`).
-   `docs/`: Contains all project documentation.
-   `src/`: Contains the Python source code, organized into modules:
    -   `main.py`: The main entry point of the application. It orchestrates the entire process from user input to running the Docker container.
        - `cli.py`: Defines the command-line interface, including all available arguments.
        - `downloader.py`: Contains functions for downloading files, such as the Minecraft server JAR.
        - `server.py`: Contains functions related to server configuration.
        - `utils.py`: A collection of helper functions used across the application.
    
    ### Command-Line Arguments
    - `--server-type`: The type of server to create. (choices: `vanilla`, `plugins`, `mods`)
    - `--server-version`: The version of the Minecraft server to install.
    - `--server-name`: Optional name for the server container and volume. Defaults to `mc-server-<version>`.
    - `--xmx`: Maximum memory allocation for the server (e.g., 1024M, 2G). Default: 1024M.
    - `--xms`: Initial memory allocation for the server (e.g., 1024M, 2G). Default: 1024M.
    
