#!/bin/bash
# Check if production environment variables are loaded correctly

echo "============================================================"
echo "Checking Production Environment Configuration"
echo "============================================================"
echo ""

# Check if .env file exists
if [ -f "/var/www/scan2food/application/scan2food/.env" ]; then
    echo "✓ .env file exists"
    echo ""
    echo "Contents:"
    cat /var/www/scan2food/application/scan2food/.env
else
    echo "✗ .env file NOT found!"
fi

echo ""
echo "============================================================"
echo "Checking if Django can connect to database"
echo "============================================================"
echo ""

cd /var/www/scan2food
source application/scan2food/venv/bin/activate

# Load environment variables
export $(cat application/scan2food/.env | xargs)

# Test Django database connection
cd application/scan2food
python manage.py check --database default

echo ""
echo "============================================================"
echo "Checking scan2food.service configuration"
echo "============================================================"
echo ""

if [ -f "/etc/systemd/system/scan2food.service" ]; then
    echo "Service file contents:"
    cat /etc/systemd/system/scan2food.service
else
    echo "✗ Service file NOT found!"
fi

echo ""
echo "============================================================"
echo "Testing actual URL"
echo "============================================================"
echo ""

# Test the actual URL that's failing
curl -I http://localhost:8000/theatre/show-menu/2442/

echo ""
echo "Done!"
