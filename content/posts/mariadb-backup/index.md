---
title: "Automating MariaDB Backups in Docker with a Shell Script"
date: 2023-04-25T12:48:00+01:00
draft: false

tags:
- home automation
- docker
- mariadb
- backup

cover:
    image: "cover.png"
    alt: "MariaDB Logo"

summary:
    Backing up your data regularly is essential, especially for critical applications like Home Assistant running MariaDB in a Docker container. This article will guide you through creating scripts that automate the backup and restoration processes, designed to be flexible by accepting arguments for the password and paths.

---
### Introduction

Backing up your data regularly is essential, especially for critical applications like Home Assistant running MariaDB in a Docker container. This article will guide you through creating scripts that automate the backup and restoration processes, designed to be flexible by accepting arguments for the password and paths.

### Prerequisites

- Docker installed and running.
- MariaDB container running with your data.

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

Now, run the script, passing the password and backup folder path as arguments:

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

### Restoring the Database from Backup


#### Restoration Script with Arguments

To simplify the restoration process, we'll create a separate shell script that accepts two arguments:

1. MariaDB password
2. Path to the backup file you want to restore

##### Script Creation

1. Create and open a new script:

```bash
nano /path_to_scripts_folder/restore_mariadb.sh
```

2. Copy and paste the following content:

```bash
#!/bin/bash

# Check if the right number of arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <password> <backup_file_path>"
    exit 1
fi

PASSWORD=$1
BACKUP_FILE=$2

gunzip < "$BACKUP_FILE" | docker exec -i mariadb /usr/bin/mysql -u homeassistant --password=$PASSWORD
```

3. Save and exit the editor.

4. Make the script executable:

```bash
chmod +x /path_to_scripts_folder/restore_mariadb.sh
```

Now, run the script, passing the password and the path to the backup file as arguments:

```bash
/path_to_scripts_folder/restore_mariadb.sh your_password /path_to_backup_folder/database_backup_YOUR_DATE.sql.gz
```

#### Notes on Restoration

1. **Backup before restore**: Always take a fresh backup before starting the restoration process. This ensures you have a fallback if the restore doesn't go as planned.
2. **Check Compatibility**: Ensure the MariaDB version you are restoring to is compatible with the version from which you took the backup.
3. **Downtime Considerations**: Depending on the size of your database and the restoration environment's performance, the restoration process might take some time. Plan accordingly.
