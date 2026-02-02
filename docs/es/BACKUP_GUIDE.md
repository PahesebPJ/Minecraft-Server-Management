# Guía de Respaldo y Restauración del Servidor de Minecraft

Esta guía explica cómo respaldar y restaurar los datos de tu servidor de Minecraft (mundos, mods, configuraciones) cuando usas Docker.

## 📋 Tabla de Contenidos

- [Entendiendo los Volúmenes de Docker](#entendiendo-los-volúmenes-de-docker)
- [Métodos de Respaldo](#métodos-de-respaldo)
- [Métodos de Restauración](#métodos-de-restauración)
- [Respaldos Automatizados](#respaldos-automatizados)
- [Mejores Prácticas](#mejores-prácticas)

---

## Entendiendo los Volúmenes de Docker

Los datos de tu servidor de Minecraft se almacenan en un **volumen de Docker** (ej., `test-fabric-server-data`). Este volumen contiene:

- 🌍 **Datos del mundo** (`/app/world/`)
- 🔧 **Mods** (`/app/mods/`)
- ⚙️ **Configuraciones del servidor** (`/app/server.properties`, etc.)
- 📝 **Registros** (`/app/logs/`)
- 💾 **Datos de jugadores** (`/app/world/playerdata/`)

**Ventaja**: ¡Respaldar el volumen respalda todo de una vez!

---

## Métodos de Respaldo

### Método 1: Respaldo Completo del Volumen (Recomendado)

Crea un archivo comprimido de todos los datos del servidor.

#### Windows (PowerShell):
```powershell
# Crear directorio de respaldos
mkdir C:\respaldos -ErrorAction SilentlyContinue

# Respaldo con marca de tiempo
docker run --rm -v test-fabric-server-data:/data -v C:\respaldos:/backup ubuntu tar czf /backup/server-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss').tar.gz -C /data .
```

#### Linux/Mac:
```bash
# Crear directorio de respaldos
mkdir -p ~/respaldos

# Respaldo con marca de tiempo
docker run --rm -v test-fabric-server-data:/data -v ~/respaldos:/backup ubuntu tar czf /backup/server-backup-$(date +%Y%m%d-%H%M%S).tar.gz -C /data .
```

**Resultado**: Crea `server-backup-20260201-205500.tar.gz` en tu carpeta de respaldos.

---

### Método 2: Copiar Carpetas Específicas

Copia solo lo que necesitas (mundo, mods, etc.) desde un contenedor en ejecución o detenido.

```bash
# Respaldar carpeta del mundo
docker cp test-fabric-server:/app/world ./respaldos/world-backup

# Respaldar carpeta de mods
docker cp test-fabric-server:/app/mods ./respaldos/mods-backup

# Respaldar propiedades del servidor
docker cp test-fabric-server:/app/server.properties ./respaldos/

# Respaldar todo
docker cp test-fabric-server:/app ./respaldos/respaldo-completo-servidor
```

**Nota**: El contenedor debe existir (puede estar detenido o en ejecución).

---

### Método 3: Exportar Volumen a Directorio

Extrae todo el contenido del volumen a un directorio local.

```bash
# Exportar volumen al directorio actual
docker run --rm -v test-fabric-server-data:/data -v ${PWD}/backup:/backup alpine cp -r /data/. /backup/

# En Windows PowerShell, usa:
docker run --rm -v test-fabric-server-data:/data -v ${PWD}\backup:/backup alpine cp -r /data/. /backup/
```

**Resultado**: Todos los archivos del servidor copiados al directorio `./backup/`.

---

### Método 4: Respaldo Manual Antes de Detener

Para máxima seguridad, detén el servidor antes de respaldar para asegurar consistencia de datos.

```bash
# 1. Detener el servidor
docker stop test-fabric-server

# 2. Crear respaldo
docker run --rm -v test-fabric-server-data:/data -v ~/respaldos:/backup ubuntu tar czf /backup/server-backup-$(date +%Y%m%d-%H%M%S).tar.gz -C /data .

# 3. Reiniciar el servidor
docker start test-fabric-server
```

---

## Métodos de Restauración

### Restaurar a Servidor Existente

Reemplaza los datos actuales del servidor con el respaldo.

```bash
# 1. Detener el servidor
docker stop test-fabric-server

# 2. Limpiar datos existentes (opcional pero recomendado)
docker run --rm -v test-fabric-server-data:/data ubuntu rm -rf /data/*

# 3. Restaurar desde respaldo
docker run --rm -v test-fabric-server-data:/data -v ~/respaldos:/backup ubuntu tar xzf /backup/server-backup-20260201-205500.tar.gz -C /data

# 4. Iniciar el servidor
docker start test-fabric-server
```

**Windows PowerShell**:
```powershell
docker stop test-fabric-server
docker run --rm -v test-fabric-server-data:/data ubuntu rm -rf /data/*
docker run --rm -v test-fabric-server-data:/data -v C:\respaldos:/backup ubuntu tar xzf /backup/server-backup-20260201-205500.tar.gz -C /data
docker start test-fabric-server
```

---

### Restaurar a Nuevo Servidor

Crea un servidor completamente nuevo desde un respaldo.

```bash
# 1. Crear nuevo volumen
docker volume create nuevo-servidor-data

# 2. Restaurar respaldo al nuevo volumen
docker run --rm -v nuevo-servidor-data:/data -v ~/respaldos:/backup ubuntu tar xzf /backup/server-backup-20260201-205500.tar.gz -C /data

# 3. Ejecutar nuevo servidor con datos restaurados
docker run -d \
  --name nuevo-servidor \
  -p 25566:25565 \
  -e EULA=TRUE \
  -e XMX=2G \
  -e XMS=1G \
  -v nuevo-servidor-data:/app \
  minecraft-mods-server:1.21.1
```

**Nota**: Puerto cambiado a 25566 para evitar conflicto con servidor existente.

---

### Restaurar Archivos/Carpetas Específicos

Restaura solo ciertas partes (ej., solo el mundo).

```bash
# 1. Extraer respaldo a ubicación temporal
mkdir temp-restore
docker run --rm -v ~/respaldos:/backup -v ${PWD}/temp-restore:/restore ubuntu tar xzf /backup/server-backup-20260201-205500.tar.gz -C /restore

# 2. Copiar carpeta específica al contenedor en ejecución
docker cp temp-restore/world test-fabric-server:/app/world

# 3. Reiniciar servidor para aplicar cambios
docker restart test-fabric-server

# 4. Limpiar
rm -rf temp-restore
```

---

## Respaldos Automatizados

### Script de Respaldo Simple

Crea un archivo `backup-server.sh` (Linux/Mac) o `backup-server.ps1` (Windows):

**Linux/Mac** (`backup-server.sh`):
```bash
#!/bin/bash

SERVER_NAME="test-fabric-server"
VOLUME_NAME="${SERVER_NAME}-data"
BACKUP_DIR="$HOME/minecraft-respaldos"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup-$DATE.tar.gz"

# Crear directorio de respaldos
mkdir -p "$BACKUP_DIR"

# Crear respaldo
echo "Creando respaldo: $BACKUP_FILE"
docker run --rm \
  -v ${VOLUME_NAME}:/data \
  -v ${BACKUP_DIR}:/backup \
  ubuntu tar czf /backup/backup-$DATE.tar.gz -C /data .

echo "Respaldo completado: $BACKUP_FILE"

# Opcional: Mantener solo los últimos 7 respaldos
cd "$BACKUP_DIR"
ls -t backup-*.tar.gz | tail -n +8 | xargs -r rm
echo "Respaldos antiguos eliminados (manteniendo últimos 7)"
```

**Windows PowerShell** (`backup-server.ps1`):
```powershell
$ServerName = "test-fabric-server"
$VolumeName = "$ServerName-data"
$BackupDir = "C:\minecraft-respaldos"
$Date = Get-Date -Format "yyyyMMdd-HHmmss"
$BackupFile = "$BackupDir\backup-$Date.tar.gz"

# Crear directorio de respaldos
New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null

# Crear respaldo
Write-Host "Creando respaldo: $BackupFile"
docker run --rm `
  -v ${VolumeName}:/data `
  -v ${BackupDir}:/backup `
  ubuntu tar czf /backup/backup-$Date.tar.gz -C /data .

Write-Host "Respaldo completado: $BackupFile"

# Opcional: Mantener solo los últimos 7 respaldos
Get-ChildItem "$BackupDir\backup-*.tar.gz" | 
  Sort-Object LastWriteTime -Descending | 
  Select-Object -Skip 7 | 
  Remove-Item
Write-Host "Respaldos antiguos eliminados (manteniendo últimos 7)"
```

**Hacer ejecutable y correr**:
```bash
# Linux/Mac
chmod +x backup-server.sh
./backup-server.sh

# Windows PowerShell
.\backup-server.ps1
```

---

### Programar Respaldos Automatizados

#### Linux/Mac (Cron)

```bash
# Editar crontab
crontab -e

# Agregar respaldo diario a las 3 AM
0 3 * * * /ruta/a/backup-server.sh

# Agregar respaldo cada 6 horas
0 */6 * * * /ruta/a/backup-server.sh
```

#### Windows (Programador de Tareas)

1. Abrir **Programador de tareas**
2. Crear tarea básica
3. Configurar activador (ej., Diario a las 3:00 AM)
4. Acción: Iniciar un programa
   - Programa: `powershell.exe`
   - Argumentos: `-File "C:\ruta\a\backup-server.ps1"`

---

## Mejores Prácticas

### ✅ Hacer

1. **Respaldar antes de cambios importantes**
   - Antes de actualizar versión de Minecraft
   - Antes de agregar/quitar mods
   - Antes de cambiar configuraciones del servidor

2. **Respaldos automatizados regulares**
   - Respaldos diarios para servidores activos
   - Semanales para servidores menos activos

3. **Probar tus respaldos**
   - Restaurar periódicamente a un servidor de prueba
   - Verificar que los datos del mundo cargan correctamente

4. **Mantener múltiples versiones de respaldo**
   - Retener al menos 7 días de respaldos
   - Mantener respaldos semanales por un mes

5. **Almacenar respaldos fuera del servidor**
   - Copiar a disco externo
   - Subir a almacenamiento en la nube (Google Drive, Dropbox, etc.)

### ❌ No Hacer

1. **No respaldar mientras el servidor está escribiendo**
   - Detén el servidor o usa la función de snapshot de Docker
   - Respaldos inconsistentes pueden corromper datos

2. **No almacenar respaldos solo en el mismo disco**
   - Falla del disco = respaldos perdidos
   - Usa almacenamiento externo

3. **No olvidar probar las restauraciones**
   - Respaldos no probados pueden no funcionar cuando se necesiten

---

## Comandos de Referencia Rápida

### Respaldo
```bash
# Respaldo rápido (Linux/Mac)
docker run --rm -v SERVER-data:/data -v ~/respaldos:/backup ubuntu tar czf /backup/backup-$(date +%Y%m%d-%H%M%S).tar.gz -C /data .

# Respaldo rápido (Windows)
docker run --rm -v SERVER-data:/data -v C:\respaldos:/backup ubuntu tar czf /backup/backup-$(Get-Date -Format 'yyyyMMdd-HHmmss').tar.gz -C /data .
```

### Restaurar
```bash
# Restauración rápida
docker stop NOMBRE-SERVIDOR
docker run --rm -v SERVER-data:/data -v ~/respaldos:/backup ubuntu tar xzf /backup/ARCHIVO-RESPALDO.tar.gz -C /data
docker start NOMBRE-SERVIDOR
```

### Listar Respaldos
```bash
# Linux/Mac
ls -lh ~/respaldos/

# Windows
dir C:\respaldos\
```

### Verificar Tamaño del Volumen
```bash
docker system df -v | grep SERVER-data
```

---

## Solución de Problemas

### El archivo de respaldo es muy grande
- Comprimir más: Usa `tar czf` (gzip) o `tar cJf` (xz)
- Excluir logs: `tar czf /backup/backup.tar.gz -C /data --exclude='logs' .`

### La restauración falla con "permiso denegado"
- Ejecuta comandos de Docker con permisos apropiados
- En Linux, puede necesitar `sudo`

### No puedo encontrar el archivo de respaldo
- Verifica la ruta del directorio de respaldos
- Verifica el nombre del volumen: `docker volume ls`

### El servidor no inicia después de restaurar
- Revisa los logs: `docker logs NOMBRE-SERVIDOR`
- Verifica que el archivo de respaldo no esté corrupto
- Asegúrate de que la versión de Minecraft coincida

---

## Recursos Adicionales

- [Documentación de Volúmenes de Docker](https://docs.docker.com/storage/volumes/)
- [Mejores Prácticas de Respaldo de Servidores de Minecraft](https://minecraft.fandom.com/wiki/Tutorials/Server_startup_script)

---

**Consejo**: Antes de cualquier actualización importante del servidor o instalación de mods, siempre crea un respaldo. ¡Toma 30 segundos y puede ahorrarte horas de trabajo!
