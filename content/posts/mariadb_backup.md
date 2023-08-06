
Certainly! Here's a comprehensive article about creating and automating a backup for MariaDB running in Docker using a script that accepts arguments:

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

### Advantages of Using Arguments

By using arguments in our backup script, we introduce the following advantages:

1. **Flexibility**: The same script can be used in various scenarios without any modifications.
2. **Readability**: Anyone who looks at the script can understand its purpose and usage quickly.
3. **Security**: While not a foolproof method, using arguments can slightly obfuscate sensitive information, making it less apparent in scripts or logs.

### Conclusion

Backing up data is an integral part of any system's maintenance. By leveraging a shell script that accepts arguments, you can automate backups for MariaDB running in Docker, ensuring that your data remains safe and up-to-date. As always, handle sensitive information, such as database passwords, with caution, and consider other security measures like Docker secrets or environment variables to further enhance protection.

---

Make sure to adjust any paths such as `/path_to_scripts_folder/` or `/path_to_backup_folder/` to fit your environment.
