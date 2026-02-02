#!/bin/bash

# EULA acceptance
if [ "$EULA" = "TRUE" ]; then
    echo "eula=true" > eula.txt
fi

# Default memory settings if not provided
XMX=${XMX:-1024M}
XMS=${XMS:-1024M}

# Detect which server JAR to use
if [ -f "fabric-server-launch.jar" ]; then
    echo "Starting Fabric server..."
    SERVER_JAR="fabric-server-launch.jar"
elif [ -f "server.jar" ]; then
    echo "Starting Forge server..."
    SERVER_JAR="server.jar"
elif [ -f "run.sh" ]; then
    echo "Starting newer Forge server with run script..."
    # Newer Forge versions use run.sh
    chmod +x run.sh
    exec ./run.sh --nogui
else
    echo "Error: No server JAR found!"
    exit 1
fi

# Start the Minecraft server
echo "Memory settings: -Xmx$XMX -Xms$XMS"
exec java -Xmx$XMX -Xms$XMS -jar $SERVER_JAR nogui
