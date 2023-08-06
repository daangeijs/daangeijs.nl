  ## Dockerized Backup and Restore System for Home Directory

Managing backups is an essential part of maintaining any computer system. With the rise of Docker, encapsulating complex operations within containers has never been easier. In this article, we'll guide you through creating a Docker-based system for backing up and restoring your `/home/user` directory, storing backups on a mounted HDD, and implementing a 30-day data retention policy.

### Prerequisites

1. Docker installed on your system.
2. A mounted HDD, for this tutorial, located at `/mnt/storage`.

### Step-by-Step Guide

#### 1. Set Up the Docker Environment:

##### Dockerfile:

We'll start with a Docker image based on the Debian slim version, equipped with essential tools for our operations:

```Dockerfile
FROM debian:bullseye-slim

RUN apt-get update && \
    apt-get install -y tar && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /backup
COPY backup_restore.sh .
ENTRYPOINT ["./backup_restore.sh"]
```

Here, we're setting up a Debian environment, installing the `tar` tool for compression, setting a working directory, and copying our backup script.

#### 2. Backup and Restore Script:

The core logic resides in our `backup_restore.sh` script, where we define the backup, restore, and cleanup functions.

```bash
#!/bin/bash

# Destination directory on the mounted HDD
BACKUP_DEST="/mnt/storage"

function backup() {
    tar czf ${BACKUP_DEST}/home_user_backup_$(date +%Y%m%d).tar.gz -C /home/user .
}

function restore() {
    local tarball=$1
    local restore_path=$2
    tar xzf ${BACKUP_DEST}/${tarball} -C ${restore_path}
}

function cleanup() {
    find ${BACKUP_DEST} -name 'home_user_backup_*.tar.gz' -mtime +30 -exec rm {} \;
}

if [ "$1" == "backup" ]; then
    backup
    cleanup
elif [ "$1" == "restore" ] && [ -n "$2" ] && [ -n "$3" ]; then
    restore $2 $3
else
    echo "Usage:"
    echo "./backup_restore.sh backup"
    echo "./backup_restore.sh restore tarball_filename /path/to/restore"
fi
```

**Functions Explained**:

- **backup()**: This function compresses and archives the `/home/user` directory into a tarball, which is saved directly to the mounted HDD.

- **restore()**: Allows the user to specify a backup tarball and restore its contents to a given directory.

- **cleanup()**: Implements the data retention policy by deleting backups older than 30 days from the mounted HDD.

#### 3. Building and Running the Docker Container:

First, build your Docker image:

```bash
docker build -t userbackuprestore:latest .
```

To run the Docker container:

- **For backup**:

```bash
docker run --rm -v /home/user:/home/user -v /mnt/storage:/mnt/storage userbackuprestore:latest backup
```

- **For restore**:

Replace `your_tarball_filename.tar.gz` with the desired backup tarball's filename and `/path/to/restore` with the directory where you want to restore.

```bash
docker run --rm -v /path/to/restore:/restore -v /mnt/storage:/mnt/storage userbackuprestore:latest restore your_tarball_filename.tar.gz /restore
```

### Concluding Thoughts:

With this Dockerized backup and restore system, you have a reliable method to safeguard your home directory. The system ensures backups are neatly stored on a mounted HDD and follows a 30-day retention policy. As an added benefit, the containerized nature of this solution means it's portable and can be implemented on any system with Docker. Whether you're a novice just starting with Docker or a seasoned professional, this solution offers a blend of simplicity and utility for backup management.
