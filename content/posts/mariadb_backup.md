---
title: "Automating MariaDB Backups in Docker with a Shell Script"
date: 2023-04-25T12:48:00+01:00
draft: false

tags:
- home automation
- docker
- mariadb
- backup

---

## Automating MariaDB Backups in Docker with a Shell Script

### Introduction

Backing up your data regularly is essential, especially for critical applications like Home Assistant running MariaDB in a Docker container. This article will guide you through creating a script that automates this backup process and is flexible enough to take arguments for the password and the backup folder path.

### Prerequisites

- Docker installed and running.
- MariaDB container running with your data.
- Basic understanding of the Linux command line.

### Backup Script with Arguments

To make our backup process versatile and reusable, we'll create a shell script that accepts two arguments:
1. MariaDB password
2. Backup folder path

#### Script Creation

1. Create and open a new script:

```bash
nano /path_to_scripts_folder/backup_mariadb.sh
```

2. Copy and paste the following content:

```bash
#!/bin/bash

# Check if the right number of arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <password> <backup_folder_path>"
    exit 1
fi

PASSWORD=$1
BACKUP_PATH=$2

docker exec mariadb /usr/bin/mysqldump -u homeassistant --password=$PASSWORD --all-databases | gzip > "$BACKUP_PATH/database_backup_$(date +\%F).sql.gz"
```

3. Save and exit the editor.

4. Make the script executable:

```bash
chmod +x /path_to_scripts_folder/backup_mariadb.sh
```

Now you can run the script, passing the password and backup folder path as arguments:

```bash
/path_to_scripts_folder/backup_mariadb.sh your_password /path_to_backup_folder/
```

### Scheduling Backups with Crontab

To automate the backup process daily:

1. Open the crontab:

```bash
crontab -e
```

2. Add the following line to run the script every day at 3 am:

```
0 3 * * * /path_to_scripts_folder/backup_mariadb.sh your_password /path_to_backup_folder/
```
