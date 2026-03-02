#!/bin/bash
# Deploy the get-db-files fix

echo "=== Deploying get-db-files fix ==="
cd /var/www/scan2food

echo ""
echo "=== Pulling latest code ==="
git pull origin main

echo ""
echo "=== Ensuring backup_db folder exists with correct permissions ==="
mkdir -p /var/www/scan2food/application/scan2food/media/backup_db
chown -R www-data:www-data /var/www/scan2food/application/scan2food/media/backup_db
chmod 755 /var/www/scan2food/application/scan2food/media/backup_db

echo ""
echo "=== Restarting Gunicorn ==="
systemctl restart gunicorn

echo ""
echo "=== Waiting 3 seconds for Gunicorn to start ==="
sleep 3

echo ""
echo "=== Testing the get-db-files endpoint ==="
echo "Visit: https://scan2food.com/admin-portal/get-db-files"
echo ""
echo "=== Checking Gunicorn status ==="
systemctl status gunicorn --no-pager -l

echo ""
echo "=== Deployment complete! ==="
echo "The route should now work properly."
