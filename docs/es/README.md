# Documentación del Proyecto

## Resumen del Proyecto

Esta herramienta proporciona una interfaz de línea de comandos (CLI) simple para automatizar la creación y gestión de un servidor de Minecraft. Utiliza Docker para crear un entorno portátil, consistente y aislado para el servidor, eliminando la necesidad de que los usuarios tengan Java instalado en sus máquinas.

El objetivo principal es simplificar el proceso de configuración a un solo comando, permitiendo a los usuarios especificar la versión del servidor y la asignación de memoria, y tener un servidor en funcionamiento en minutos.

## Cómo Funciona

El flujo de trabajo de la herramienta está orquestado por el script principal de Python (`src/main.py`) y gira en torno a Docker.

1.  **Entrada del Usuario**: El script primero analiza los argumentos proporcionados por el usuario desde la línea de comandos, como el tipo de servidor, la versión y la configuración de memoria (`--xmx`, `--xms`).

2.  **Descarga**: Descarga el archivo JAR oficial del servidor de Minecraft correspondiente a la versión seleccionada por el usuario.

3.  **Contexto de Compilación de Docker**: Se crea un directorio temporal (`docker_build_context`). El script copia lo siguiente en este directorio:
    *   El `server.jar` descargado.
    *   El `Dockerfile` del proyecto.
    *   El script `entrypoint.sh`.

4.  **Compilación de la Imagen de Docker**: El script luego invoca `docker build`. Docker usa el `Dockerfile` en el contexto de compilación para crear una nueva imagen de Docker. El `Dockerfile` especifica la imagen base de Java, copia el `server.jar` y `entrypoint.sh` en la imagen y establece el punto de entrada.

5.  **Ejecución del Contenedor de Docker**: Una vez que se compila la imagen, el script ejecuta un nuevo contenedor de Docker a partir de ella usando `docker run`. Pasa varios parámetros importantes:
    *   **Variables de Entorno**: Establece `EULA=TRUE`, `XMX` y `XMS` como variables de entorno dentro del contenedor.
    *   **Mapeo de Puertos**: Mapea el puerto `25565` en el host al puerto `25565` en el contenedor, permitiendo a los usuarios conectarse al servidor de Minecraft.
    *   **Montaje de Volumen**: Crea y monta un volumen de Docker. Esto es crucial para persistir los datos del servidor (archivos del mundo, datos de jugadores, etc.) incluso si se elimina el contenedor.

6.  **Inicialización del Contenedor**: Cuando el contenedor se inicia, ejecuta automáticamente el script `entrypoint.sh`, que:
    *   Acepta el EULA en nombre del usuario.
    *   Inicia el servidor de Minecraft utilizando la configuración de memoria especificada.

7.  **Limpieza**: Finalmente, el script principal de Python elimina el directorio temporal `docker_build_context`, dejando el sistema limpio.

## Estructura del Proyecto

-   `Dockerfile`: La receta para construir la imagen de Docker del servidor de Minecraft. Especifica la imagen base de Java, copia los archivos necesarios y establece el punto de entrada del contenedor.
-   `entrypoint.sh`: Un script de shell que se ejecuta cuando se inicia el contenedor de Docker. Se encarga de la aceptación del EULA y de iniciar el proceso de Java para el servidor de Minecraft.
-   `requirements.txt`: Enumera las dependencias de Python requeridas para el proyecto.
-   `.gitignore`: Especifica los archivos y directorios que deben ser ignorados por Git (por ejemplo, `venv`).
-   `docs/`: Contiene toda la documentación del proyecto.
-   `src/`: Contiene el código fuente de Python, organizado en módulos:
    -   `main.py`: El punto de entrada principal de la aplicación. Orquesta todo el proceso, desde la entrada del usuario hasta la ejecución del contenedor de Docker.
        - `cli.py`: Define la interfaz de línea de comandos, incluidos todos los argumentos disponibles.
        - `downloader.py`: Contiene funciones para descargar archivos, como el JAR del servidor de Minecraft.
        - `server.py`: Contiene funciones relacionadas con la configuración del servidor.
        - `utils.py`: Una colección de funciones de ayuda utilizadas en toda la aplicación.
    
    ### Argumentos de Línea de Comandos
    - `--server-type`: El tipo de servidor a crear. (opciones: `vanilla`, `plugins`, `mods`)
    - `--server-version`: La versión del servidor de Minecraft a instalar.
    - `--server-name`: Nombre opcional para el contenedor y el volumen del servidor. Por defecto es `mc-server-<version>`.
    - `--xmx`: Asignación máxima de memoria para el servidor (p. ej., 1024M, 2G). Por defecto: 1024M.
    - `--xms`: Asignación inicial de memoria para el servidor (p. ej., 1024M, 2G). Por defecto: 1024M.
    
