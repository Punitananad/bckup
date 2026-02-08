#!/bin/bash

# RESTART DAPHNE AND NGINX
# sudo systemctl restart daphne
# sudo systemctl restart nginx


# run backup script
# python main.py
/home/guru/myenv/bin/python3 /home/guru/backup_script/db-backup/main.py

# enter log file
echo "service start at - $(date)" >>  /home/guru/cron_log.txt

