#!/bin/bash
# Fix Static Files on Production Server
# Run this script on your SSH server

set -e  # Exit on any error

echo "=========================================="
echo "Fixing Static Files on Production Server"
echo "=========================================="
echo ""

# Configuration - Update these paths if needed
APP_DIR="/var/www/scan2food/application/scan2food"
STATIC_ROOT="/var/www/scan2food/static"
VENV_PATH="/var/www/scan2food/venv"

echo "Step 1: Activating virtual environment..."
source $VENV_PATH/bin/activate

echo "Step 2: Navigating to application directory..."
cd $APP_DIR

echo "Step 3: Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Step 4: Setting correct permissions..."
sudo chown -R www-data:www-data $STATIC_ROOT
sudo chmod -R 755 $STATIC_ROOT

echo "Step 5: Verifying static files exist..."
if [ -d "$STATIC_ROOT/assets" ]; then
    echo "✓ assets/ directory found"
else
    echo "✗ WARNING: assets/ directory not found!"
fi

if [ -d "$STATIC_ROOT/theatre_js" ]; then
    echo "✓ theatre_js/ directory found"
else
    echo "✗ WARNING: theatre_js/ directory not found!"
fi

echo ""
echo "Step 6: Checking Nginx configuration..."
if [ -f "/etc/nginx/sites-available/scan2food" ]; then
    echo "✓ Nginx config file exists"
    echo ""
    echo "Checking for static location block..."
    if grep -q "location /static/" /etc/nginx/sites-available/scan2food; then
        echo "✓ Static location block found in Nginx config"
    else
        echo "✗ WARNING: Static location block NOT found in Nginx config!"
        echo ""
        echo "Add this to your Nginx config:"
        echo ""
        echo "location /static/ {"
        echo "    alias /var/www/scan2food/static/;"
        echo "    expires 30d;"
        echo "    add_header Cache-Control \"public, immutable\";"
        echo "}"
    fi
else
    echo "✗ WARNING: Nginx config file not found at /etc/nginx/sites-available/scan2food"
fi

echo ""
echo "Step 7: Testing Nginx configuration..."
sudo nginx -t

echo ""
echo "Step 8: Restarting services..."
sudo systemctl restart nginx
echo "✓ Nginx restarted"

# Restart Gunicorn if it's running
if systemctl is-active --quiet gunicorn; then
    sudo systemctl restart gunicorn
    echo "✓ Gunicorn restarted"
fi

# Restart Daphne if it's running
if systemctl is-active --quiet daphne; then
    sudo systemctl restart daphne
    echo "✓ Daphne restarted"
fi

echo ""
echo "=========================================="
echo "Static Files Fix Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Clear your browser cache (Ctrl + Shift + Delete)"
echo "2. Test accessing: https://calculatentrade.com/static/assets/css/style.css"
echo "3. Reload your page: https://calculatentrade.com/theatre/live-orders/"
echo ""
echo "If issues persist, check:"
echo "  - Nginx error log: sudo tail -f /var/log/nginx/error.log"
echo "  - Application log: sudo journalctl -u gunicorn -f"
echo ""
