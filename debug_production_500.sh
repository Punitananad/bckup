#!/bin/bash
# Debug script for 500 error on production

echo "=== Checking Django Error Logs ==="
# Check if there are any recent error logs
if [ -f "/var/www/scan2food/guru.log" ]; then
    echo "Last 50 lines of guru.log:"
    tail -n 50 /var/www/scan2food/guru.log
fi

echo ""
echo "=== Checking Gunicorn/Daphne Logs ==="
# Check systemd service logs
sudo journalctl -u gunicorn -n 50 --no-pager
sudo journalctl -u daphne -n 50 --no-pager

echo ""
echo "=== Checking Nginx Error Logs ==="
sudo tail -n 50 /var/log/nginx/error.log

echo ""
echo "=== Checking Django Settings ==="
cd /var/www/scan2food
source venv/bin/activate
python application/scan2food/manage.py check --deploy

echo ""
echo "=== Testing Database Connection ==="
python application/scan2food/manage.py dbshell --command="SELECT 1;"

echo ""
echo "=== Checking Static Files ==="
ls -la /var/www/scan2food/static_files/scan2food-static/static/
