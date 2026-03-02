#!/bin/bash
# Quick deployment script for backup system

echo "=== Deploying Automated Backup System ==="
echo ""

# On deployment server, run these commands:
cat << 'EOF'
Run these commands on your server (165.22.219.111):

1. Pull latest code:
   cd /var/www/scan2food
   git pull origin main

2. Setup automated backups:
   chmod +x setup_backup_cron.sh
   sudo bash setup_backup_cron.sh

3. Verify installation:
   crontab -l | grep backup

4. Check first backup:
   ls -lh /var/www/scan2food/application/scan2food/media/backup_db/

5. View in browser:
   https://scan2food.com/admin-portal/get-db-files

Done! Backups will run automatically at 4:00 AM daily.
EOF
