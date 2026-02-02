# Minecraft Server Backup & Restore Guide

This guide explains how to backup and restore your Minecraft server data (worlds, mods, configurations) when using Docker.

## 📋 Table of Contents

- [Understanding Docker Volumes](#understanding-docker-volumes)
- [Backup Methods](#backup-methods)
- [Restore Methods](#restore-methods)
- [Automated Backups](#automated-backups)
- [Best Practices](#best-practices)

---

## Understanding Docker Volumes

Your Minecraft server data is stored in a **Docker volume** (e.g., `test-fabric-server-data`). This volume contains:

- 🌍 **World data** (`/app/world/`)
- 🔧 **Mods** (`/app/mods/`)
- ⚙️ **Server configurations** (`/app/server.properties`, etc.)
- 📝 **Logs** (`/app/logs/`)
- 💾 **Player data** (`/app/world/playerdata/`)

**Advantage**: Backing up the volume backs up everything in one go!

---

## Backup Methods

### Method 1: Full Volume Backup (Recommended)

Creates a compressed archive of the entire server data.

#### Windows (PowerShell):
```powershell
# Create backup directory
mkdir C:\backups -ErrorAction SilentlyContinue

# Backup with timestamp
docker run --rm -v test-fabric-server-data:/data -v C:\backups:/backup ubuntu tar czf /backup/server-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss').tar.gz -C /data .
```

#### Linux/Mac:
```bash
# Create backup directory
mkdir -p ~/backups

# Backup with timestamp
docker run --rm -v test-fabric-server-data:/data -v ~/backups:/backup ubuntu tar czf /backup/server-backup-$(date +%Y%m%d-%H%M%S).tar.gz -C /data .
```

**Result**: Creates `server-backup-20260201-205500.tar.gz` in your backups folder.

---

### Method 2: Copy Specific Folders

Copy only what you need (world, mods, etc.) from a running or stopped container.

```bash
# Backup world folder
docker cp test-fabric-server:/app/world ./backups/world-backup

# Backup mods folder
docker cp test-fabric-server:/app/mods ./backups/mods-backup

# Backup server properties
docker cp test-fabric-server:/app/server.properties ./backups/

# Backup everything
docker cp test-fabric-server:/app ./backups/full-server-backup
```

**Note**: Container must exist (can be stopped or running).

---

### Method 3: Export Volume to Directory

Extract the entire volume contents to a local directory.

```bash
# Export volume to current directory
docker run --rm -v test-fabric-server-data:/data -v ${PWD}/backup:/backup alpine cp -r /data/. /backup/

# On Windows PowerShell, use:
docker run --rm -v test-fabric-server-data:/data -v ${PWD}\backup:/backup alpine cp -r /data/. /backup/
```

**Result**: All server files copied to `./backup/` directory.

---

### Method 4: Manual Backup Before Stopping

For maximum safety, stop the server before backing up to ensure data consistency.

```bash
# 1. Stop the server
docker stop test-fabric-server

# 2. Create backup
docker run --rm -v test-fabric-server-data:/data -v ~/backups:/backup ubuntu tar czf /backup/server-backup-$(date +%Y%m%d-%H%M%S).tar.gz -C /data .

# 3. Restart the server
docker start test-fabric-server
```

---

## Restore Methods

### Restore to Existing Server

Replace current server data with backup.

```bash
# 1. Stop the server
docker stop test-fabric-server

# 2. Clear existing data (optional but recommended)
docker run --rm -v test-fabric-server-data:/data ubuntu rm -rf /data/*

# 3. Restore from backup
docker run --rm -v test-fabric-server-data:/data -v ~/backups:/backup ubuntu tar xzf /backup/server-backup-20260201-205500.tar.gz -C /data

# 4. Start the server
docker start test-fabric-server
```

**Windows PowerShell**:
```powershell
docker stop test-fabric-server
docker run --rm -v test-fabric-server-data:/data ubuntu rm -rf /data/*
docker run --rm -v test-fabric-server-data:/data -v C:\backups:/backup ubuntu tar xzf /backup/server-backup-20260201-205500.tar.gz -C /data
docker start test-fabric-server
```

---

### Restore to New Server

Create a completely new server from a backup.

```bash
# 1. Create new volume
docker volume create new-server-data

# 2. Restore backup to new volume
docker run --rm -v new-server-data:/data -v ~/backups:/backup ubuntu tar xzf /backup/server-backup-20260201-205500.tar.gz -C /data

# 3. Run new server with restored data
docker run -d \
  --name new-server \
  -p 25566:25565 \
  -e EULA=TRUE \
  -e XMX=2G \
  -e XMS=1G \
  -v new-server-data:/app \
  minecraft-mods-server:1.21.1
```

**Note**: Changed port to 25566 to avoid conflict with existing server.

---

### Restore Specific Files/Folders

Restore only certain parts (e.g., just the world).

```bash
# 1. Extract backup to temporary location
mkdir temp-restore
docker run --rm -v ~/backups:/backup -v ${PWD}/temp-restore:/restore ubuntu tar xzf /backup/server-backup-20260201-205500.tar.gz -C /restore

# 2. Copy specific folder to running container
docker cp temp-restore/world test-fabric-server:/app/world

# 3. Restart server to apply changes
docker restart test-fabric-server

# 4. Clean up
rm -rf temp-restore
```

---

## Automated Backups

### Simple Backup Script

Create a file `backup-server.sh` (Linux/Mac) or `backup-server.ps1` (Windows):

**Linux/Mac** (`backup-server.sh`):
```bash
#!/bin/bash

SERVER_NAME="test-fabric-server"
VOLUME_NAME="${SERVER_NAME}-data"
BACKUP_DIR="$HOME/minecraft-backups"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup-$DATE.tar.gz"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Create backup
echo "Creating backup: $BACKUP_FILE"
docker run --rm \
  -v ${VOLUME_NAME}:/data \
  -v ${BACKUP_DIR}:/backup \
  ubuntu tar czf /backup/backup-$DATE.tar.gz -C /data .

echo "Backup completed: $BACKUP_FILE"

# Optional: Keep only last 7 backups
cd "$BACKUP_DIR"
ls -t backup-*.tar.gz | tail -n +8 | xargs -r rm
echo "Old backups cleaned up (keeping last 7)"
```

**Windows PowerShell** (`backup-server.ps1`):
```powershell
$ServerName = "test-fabric-server"
$VolumeName = "$ServerName-data"
$BackupDir = "C:\minecraft-backups"
$Date = Get-Date -Format "yyyyMMdd-HHmmss"
$BackupFile = "$BackupDir\backup-$Date.tar.gz"

# Create backup directory
New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null

# Create backup
Write-Host "Creating backup: $BackupFile"
docker run --rm `
  -v ${VolumeName}:/data `
  -v ${BackupDir}:/backup `
  ubuntu tar czf /backup/backup-$Date.tar.gz -C /data .

Write-Host "Backup completed: $BackupFile"

# Optional: Keep only last 7 backups
Get-ChildItem "$BackupDir\backup-*.tar.gz" | 
  Sort-Object LastWriteTime -Descending | 
  Select-Object -Skip 7 | 
  Remove-Item
Write-Host "Old backups cleaned up (keeping last 7)"
```

**Make executable and run**:
```bash
# Linux/Mac
chmod +x backup-server.sh
./backup-server.sh

# Windows PowerShell
.\backup-server.ps1
```

---

### Schedule Automated Backups

#### Linux/Mac (Cron)

```bash
# Edit crontab
crontab -e

# Add daily backup at 3 AM
0 3 * * * /path/to/backup-server.sh

# Add backup every 6 hours
0 */6 * * * /path/to/backup-server.sh
```

#### Windows (Task Scheduler)

1. Open **Task Scheduler**
2. Create Basic Task
3. Set trigger (e.g., Daily at 3:00 AM)
4. Action: Start a program
   - Program: `powershell.exe`
   - Arguments: `-File "C:\path\to\backup-server.ps1"`

---

## Best Practices

### ✅ Do's

1. **Backup before major changes**
   - Before updating Minecraft version
   - Before adding/removing mods
   - Before changing server configurations

2. **Regular automated backups**
   - Daily backups for active servers
   - Weekly for less active servers

3. **Test your backups**
   - Periodically restore to a test server
   - Verify world data loads correctly

4. **Keep multiple backup versions**
   - Retain at least 7 days of backups
   - Keep weekly backups for a month

5. **Store backups off-server**
   - Copy to external drive
   - Upload to cloud storage (Google Drive, Dropbox, etc.)

### ❌ Don'ts

1. **Don't backup while server is writing**
   - Stop server or use Docker's snapshot feature
   - Inconsistent backups can corrupt data

2. **Don't store backups only on same disk**
   - Disk failure = lost backups
   - Use external storage

3. **Don't forget to test restores**
   - Untested backups might not work when needed

---

## Quick Reference Commands

### Backup
```bash
# Quick backup (Linux/Mac)
docker run --rm -v SERVER-data:/data -v ~/backups:/backup ubuntu tar czf /backup/backup-$(date +%Y%m%d-%H%M%S).tar.gz -C /data .

# Quick backup (Windows)
docker run --rm -v SERVER-data:/data -v C:\backups:/backup ubuntu tar czf /backup/backup-$(Get-Date -Format 'yyyyMMdd-HHmmss').tar.gz -C /data .
```

### Restore
```bash
# Quick restore
docker stop SERVER-name
docker run --rm -v SERVER-data:/data -v ~/backups:/backup ubuntu tar xzf /backup/BACKUP-FILE.tar.gz -C /data
docker start SERVER-name
```

### List Backups
```bash
# Linux/Mac
ls -lh ~/backups/

# Windows
dir C:\backups\
```

### Check Volume Size
```bash
docker system df -v | grep SERVER-data
```

---

## Troubleshooting

### Backup file is too large
- Compress more: Use `tar czf` (gzip) or `tar cJf` (xz)
- Exclude logs: `tar czf /backup/backup.tar.gz -C /data --exclude='logs' .`

### Restore fails with "permission denied"
- Run Docker commands with appropriate permissions
- On Linux, may need `sudo`

### Can't find backup file
- Check backup directory path
- Verify volume name: `docker volume ls`

### Server won't start after restore
- Check logs: `docker logs SERVER-name`
- Verify backup file isn't corrupted
- Ensure Minecraft version matches

---

## Additional Resources

- [Docker Volume Documentation](https://docs.docker.com/storage/volumes/)
- [Minecraft Server Backup Best Practices](https://minecraft.fandom.com/wiki/Tutorials/Server_startup_script)

---

**Tip**: Before any major server update or mod installation, always create a backup. It takes 30 seconds and can save hours of work!
