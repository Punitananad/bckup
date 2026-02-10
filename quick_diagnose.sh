#!/bin/bash
# Quick diagnostic script for 500 error

echo "=========================================="
echo "SCAN2FOOD 500 ERROR DIAGNOSTIC"
echo "=========================================="
echo ""

# Activate virtual environment
cd /var/www/scan2food
source venv/bin/activate

echo "1. Checking Django application logs..."
echo "=========================================="
if [ -f "guru.log" ]; then
    echo "Last 30 lines of guru.log:"
    tail -n 30 guru.log
else
    echo "guru.log not found in /var/www/scan2food"
fi

if [ -f "application/scan2food/guru.log" ]; then
    echo ""
    echo "Last 30 lines of application/scan2food/guru.log:"
    tail -n 30 application/scan2food/guru.log
fi

echo ""
echo "2. Checking Gunicorn service..."
echo "=========================================="
sudo systemctl status gunicorn --no-pager | head -n 20
echo ""
echo "Recent Gunicorn logs:"
sudo journalctl -u gunicorn -n 20 --no-pager

echo ""
echo "3. Checking Daphne service..."
echo "=========================================="
sudo systemctl status daphne --no-pager | head -n 20
echo ""
echo "Recent Daphne logs:"
sudo journalctl -u daphne -n 20 --no-pager

echo ""
echo "4. Checking Nginx error logs..."
echo "=========================================="
sudo tail -n 20 /var/log/nginx/error.log

echo ""
echo "5. Checking environment file..."
echo "=========================================="
if [ -f "application/scan2food/.env" ]; then
    echo ".env file exists"
    echo "Checking for required variables (values hidden):"
    grep -E "^(SECRET_KEY|DATABASE_URL|DEBUG|ALLOWED_HOSTS)" application/scan2food/.env | sed 's/=.*/=***HIDDEN***/'
else
    echo "WARNING: .env file not found!"
fi

echo ""
echo "6. Running Django check..."
echo "=========================================="
cd application/scan2food
python manage.py check

echo ""
echo "=========================================="
echo "DIAGNOSTIC COMPLETE"
echo "=========================================="
