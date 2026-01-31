#!/bin/bash

# EULA acceptance
if [ "$EULA" = "TRUE" ]; then
    echo "eula=true" > eula.txt
fi

# Default memory settings if not provided
XMX=${XMX:-1024M}
XMS=${XMS:-1024M}

# Start the Minecraft server
java -Xmx$XMX -Xms$XMS -jar server.jar nogui
