---
title: "Dockerized Backup and Restore System for Home Directory"
date: 2023-05-25T12:48:00+01:00
draft: false

tags:
- ubuntu
- docker
- home automation
- backup

cover:
    image: "cover.png"
    alt: "Docker Logo"
    
summary:
  Managing backups is an essential part of maintaining any computer system. With the rise of Docker, encapsulating complex operations within containers has never been easier. In this article, we'll guide you through creating a Docker-based system for backing up and restoring your `/home/user` directory, storing backups on a mounted HDD, and implementing a 30-day data retention policy. Later, we will discuss how to automate this backup process using `crontab`.
---
### Introduction
Managing backups is an essential part of maintaining any computer system. With the rise of Docker, encapsulating complex operations within containers has never been easier. In this article, we'll guide you through creating a Docker-based system for backing up and restoring your `/home/user` directory, storing backups on a mounted HDD, and implementing a 30-day data retention policy. Later, we will discuss how to automate this backup process using `crontab`.

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
COPY .. .
RUN chmod +x backup_restore.sh
ENTRYPOINT ["./backup_restore.sh"]
```

Here, we're setting up a Debian environment, installing the `tar` tool for compression, setting a working directory, and copying our backup script.

#### 2. Backup and Restore Script:

The core logic resides in our `backup_restore.sh` script, where we define the backup, restore, and cleanup functions.

```bash
#!/bin/bash

# Destination directory on the mounted HDD
BACKUP_DEST="/mnt/storage/backup"
BACKUP_TARGET_PATH="/home/daan"

function backup() {
    tar czf ${BACKUP_DEST}/homeserver_backup_$(date +%Y%m%d).tar.gz -C ${BACKUP_TARGET_PATH} .
}

function restore() {
    local tarball=$1
    local restore_path=$2
    tar xzf ${BACKUP_DEST}/${tarball} -C ${restore_path}
}

function cleanup() {
    find ${BACKUP_DEST} -name 'homeserver_backup_*.tar.gz' -mtime +30 -exec rm {} \;
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

### Automating Backups Using Crontab:

After setting up the Docker-based backup system, automating the process ensures that backups are taken regularly without manual intervention. The `cron` job scheduler is an excellent tool for this. Here’s how you can schedule the backup task using `crontab`.

#### 1. Open Crontab:

To edit the current user's `crontab` entries, use:

```bash
crontab -e
```

This will open up the default editor, often `vi` or `nano`, depending on the system setup.

#### 2. Add a Cron Job:

To run the backup daily at, say, 2:30 AM, add the following line:

```bash
30 2 * * * docker run --rm -v /home/user:/home/user -v /mnt/storage:/mnt/storage userbackuprestore:latest backup
```

The general format of a cron job is:

```bash
[min] [hour] [day of month] [month] [day of week] [command]
```

For this job:

- `30` is the minute (30 minutes past the hour).
- `2` is the hour (2 AM).
- `*` for day of month, month, and day of week indicates "every" or "any."

Therefore, `30 2 * * *` means "2:30 AM, every day."

#### 3. Save and Exit:

After adding the line:

- If you're in `vi`, press `Esc`, type `:wq`, and press `Enter`.
- If you're in `nano`, press `CTRL + X`, press `Y` to confirm changes, and press `Enter` to save.

#### 4. Verify the Cron Job:

To ensure your cron job has been set correctly, you can display the current user's `crontab` entries:

```bash
crontab -l
```

You should see the line you added for the backup
