#!/bin/bash

# Automated deployment script for Scan2Food production server
# This script: backs up code, pulls latest changes, restarts services

SERVER="165.22.219.111"
PROJECT_PATH="/var/www/scan2food"
BACKUP_DIR="/var/www/scan2food_backups"

echo "============================================================"
echo "Deploying to Production Server"
echo "============================================================"
echo ""

ssh root@$SERVER << 'ENDSSH'

echo "Step 1: Creating backup directory..."
mkdir -p /var/www/scan2food_backups
cd /var/www/scan2food

echo ""
echo "Step 2: Creating backup of current code..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="/var/www/scan2food_backups/backup_${TIMESTAMP}.tar.gz"
tar -czf $BACKUP_FILE --exclude='*.pyc' --exclude='__pycache__' --exclude='*.log' --exclude='db.sqlite3' .
echo "✓ Backup created: $BACKUP_FILE"

echo ""
echo "Step 3: Pulling latest code from repository..."
git fetch origin
git reset --hard origin/main
echo "✓ Code updated"

echo ""
echo "Step 4: Restarting services..."
systemctl restart gunicorn
systemctl restart nginx
systemctl restart daphne
echo "✓ Services restarted"

echo ""
echo "Step 5: Checking service status..."
echo ""
echo "Gunicorn status:"
systemctl status gunicorn --no-pager | head -n 5
echo ""
echo "Nginx status:"
systemctl status nginx --no-pager | head -n 5
echo ""
echo "Daphne status:"
systemctl status daphne --no-pager | head -n 5

echo ""
echo "============================================================"
echo "Deployment completed successfully!"
echo "============================================================"
echo "Backup saved: $BACKUP_FILE"
echo "Latest 5 backups:"
ls -lt /var/www/scan2food_backups/*.tar.gz | head -n 5

ENDSSH

echo ""
echo "============================================================"
echo "Deployment finished!"
echo "============================================================"
echo ""
echo "Your changes are now live at: https://scan2food.com"
echo ""
