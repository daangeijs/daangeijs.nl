Certainly! Here's the revised article:

---

## Daily Backup of Home Assistant MariaDB Database in Docker

### Introduction

This guide will show you how to create daily backups of the MariaDB database used by Home Assistant running inside a Docker container. Regular backups are essential to prevent potential data loss, and automating the process ensures you always have a fresh backup.

### Prerequisites

- Docker installed and running.
- MariaDB container running with your Home Assistant data.
- Familiarity with the Linux command line.

### Backup the Database

To backup your MariaDB database running in Docker, we'll use the `mysqldump` tool. This tool creates a logical backup of the database, which you can use to restore your data later.

Execute the following command:

```bash
docker exec mariadb /usr/bin/mysqldump -u homeassistant --password=your_password --all-databases | gzip > /path_to_backup_folder/database_backup.sql.gz
```

Replace `your_password` with your MariaDB password and `/path_to_backup_folder/` with the location where you want to save your backup.

### Restore from Backup

If you need to restore your data from the backup, use the following command:

```bash
gunzip < /path_to_backup_folder/database_backup.sql.gz | docker exec -i mariadb /usr/bin/mysql -u homeassistant --password=your_password
```

Replace `/path_to_backup_folder/` with the location of your backup and `your_password` with your MariaDB password.

### Automating the Backup Using a Shell Script

To simplify the backup process and make the crontab more readable, you can create a shell script that contains the backup command.

1. Create a new script:

```bash
nano /path_to_scripts_folder/backup_mariadb.sh
```

2. Add the following content:

```bash
#!/bin/bash

docker exec mariadb /usr/bin/mysqldump -u homeassistant --password=your_password --all-databases | gzip > /path_to_backup_folder/database_backup_$(date +\%F).sql.gz
```

3. Make the script executable:

```bash
chmod +x /path_to_scripts_folder/backup_mariadb.sh
```

### Scheduling with Crontab

Now, instead of adding the entire command to the crontab, you can simply reference this script.

1. Open the crontab with:

```bash
crontab -e
```

2. Add the following line to schedule the backup script to run every day at 3 am:

```
0 3 * * * /path_to_scripts_folder/backup_mariadb.sh
```

This approach keeps the crontab clean and allows you to easily modify the backup process in the future by just updating the script.

### Conclusion

It's crucial to maintain regular backups of your data, especially for vital applications like Home Assistant. This guide offers a streamlined method to backup and restore your MariaDB data within Docker, along with a way to automate the process neatly. With the automation in place, you can rest assured, knowing your data is backed up daily.

---

Please adjust paths such as `/path_to_backup_folder/` and `/path_to_scripts_folder/` as per your requirements. As always, handle your database password with caution. Consider Docker secrets, environment variables, or other secure methods to manage sensitive data.
