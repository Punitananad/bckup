▶️ How to Run

Run the script manually:

```
python3 backup.py
```

After running, your backup file will appear in your BACKUP_DIR directory.


## ⏰ Automating with Cron (Optional)

You can schedule this script to run daily / hourly using cron.

1. Create a cron job file `backup_cron.sh` using command

`vim backup_cron.sh`

2. copy the content inside the `backup_cron.sh` file

```
#!/bin/bash

# RUN THE PYTHON SCRIPT

/home/guru/myenv/bin/python3 /home/user/database_backup_scripts/backup.py

# enter log file
echo "backup taken at - $(date)" >>  /home/guru/cron_log.txt

```

3. ✅ Give Execute Permission to the `backup_cron.sh` file by command.

`chmod +x /home/user/database_backup_scripts/cron_job.sh`

4. ✅ Add It to Cron

`crontab -e`

Add:
`0 3 * * * /home/user/database_backup_scripts/cron_job.sh`