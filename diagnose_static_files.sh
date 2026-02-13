#!/bin/bash
# Diagnose Static Files Issues on Production Server

echo "=========================================="
echo "Static Files Diagnostic Report"
echo "=========================================="
echo ""

# Configuration
APP_DIR="/root/application/scan2food"
STATIC_ROOT="/var/www/scan2food/static"
VENV_PATH="/root/venv"

echo "1. Checking Application Directory..."
if [ -d "$APP_DIR" ]; then
    echo "✓ Application directory exists: $APP_DIR"
else
    echo "✗ Application directory NOT found: $APP_DIR"
fi

echo ""
echo "2. Checking Virtual Environment..."
if [ -d "$VENV_PATH" ]; then
    echo "✓ Virtual environment exists: $VENV_PATH"
else
    echo "✗ Virtual environment NOT found: $VENV_PATH"
fi

echo ""
echo "3. Checking Static Root Directory..."
if [ -d "$STATIC_ROOT" ]; then
    echo "✓ Static root exists: $STATIC_ROOT"
    echo ""
    echo "Static files structure:"
    ls -lh $STATIC_ROOT | head -20
else
    echo "✗ Static root NOT found: $STATIC_ROOT"
    echo "  Creating directory..."
    sudo mkdir -p $STATIC_ROOT
fi

echo ""
echo "4. Checking Django Settings..."
cd $APP_DIR
source $VENV_PATH/bin/activate
python -c "
import os
import sys
sys.path.insert(0, '$APP_DIR')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theatreApp.settings')
import django
django.setup()
from django.conf import settings
print(f'STATIC_URL: {settings.STATIC_URL}')
print(f'STATIC_ROOT: {settings.STATIC_ROOT}')
print(f'STATICFILES_DIRS: {settings.STATICFILES_DIRS}')
"

echo ""
echo "5. Checking Nginx Configuration..."
if [ -f "/etc/nginx/sites-available/scan2food" ]; then
    echo "✓ Nginx config exists"
    echo ""
    echo "Static location configuration:"
    grep -A 5 "location /static/" /etc/nginx/sites-available/scan2food || echo "✗ No static location block found!"
else
    echo "✗ Nginx config NOT found"
fi

echo ""
echo "6. Checking Nginx Status..."
if systemctl is-active --quiet nginx; then
    echo "✓ Nginx is running"
else
    echo "✗ Nginx is NOT running"
fi

echo ""
echo "7. Checking Gunicorn Status..."
if systemctl is-active --quiet gunicorn; then
    echo "✓ Gunicorn is running"
else
    echo "✗ Gunicorn is NOT running"
fi

echo ""
echo "8. Checking Daphne Status..."
if systemctl is-active --quiet daphne; then
    echo "✓ Daphne is running"
else
    echo "✗ Daphne is NOT running"
fi

echo ""
echo "9. Checking File Permissions..."
if [ -d "$STATIC_ROOT" ]; then
    echo "Static root permissions:"
    ls -ld $STATIC_ROOT
    echo ""
    echo "Sample file permissions:"
    find $STATIC_ROOT -type f | head -5 | xargs ls -l
fi

echo ""
echo "10. Testing Static File Access..."
echo "Try accessing these URLs in your browser:"
echo "  - https://calculatentrade.com/static/assets/css/style.css"
echo "  - https://calculatentrade.com/static/theatre_js/menu.js"
echo ""

echo "=========================================="
echo "Diagnostic Complete"
echo "=========================================="
echo ""
echo "To fix issues, run: bash fix_production_static_files.sh"
echo ""
