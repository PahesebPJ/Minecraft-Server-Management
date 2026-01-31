# Use an official OpenJDK runtime as a parent image
FROM eclipse-temurin:17-jdk-jammy

# Set the working directory in the container
WORKDIR /app

# Expose the Minecraft server port
EXPOSE 25565

# Copy the server JAR file into the container (this will be replaced by the actual JAR later)
COPY server.jar server.jar

# Copy the entrypoint script
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Define the entrypoint for the container
ENTRYPOINT ["entrypoint.sh"]
