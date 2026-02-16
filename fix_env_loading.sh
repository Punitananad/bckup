#!/bin/bash
# Fix Environment Variable Loading Issue

echo "=== FIXING ENVIRONMENT VARIABLE LOADING ==="
echo ""

# Check current .env file
echo "1. Checking .env file..."
if [ -f "/var/www/scan2food/application/scan2food/.env" ]; then
    echo "   ✓ .env file exists"
    echo "   API_KEY in .env:"
    grep "API_KEY=" /var/www/scan2food/application/scan2food/.env | sed 's/=.*/=***HIDDEN***/'
else
    echo "   ✗ .env file NOT FOUND!"
    exit 1
fi
echo ""

# Test if Django can load the API_KEY
echo "2. Testing if Django loads API_KEY from .env..."
cd /var/www/scan2food/application/scan2food
source venv/bin/activate

# Set environment variable manually for this test
export $(grep -v '^#' .env | xargs)

python << 'EOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theatreApp.settings')
django.setup()
from django.conf import settings

print(f"   API_KEY from settings: {settings.API_KEY[:20]}...")
print(f"   API_KEY from os.environ: {os.environ.get('API_KEY', 'NOT SET')[:20]}...")

if settings.API_KEY.startswith('CHANGE_THIS'):
    print("   ✗ ERROR: API_KEY not loaded from .env!")
    print("   Django is using default value from settings.py")
else:
    print("   ✓ API_KEY loaded correctly")
EOF
echo ""

# The issue: Gunicorn's EnvironmentFile directive might not be working
echo "3. Checking Gunicorn service file..."
grep "EnvironmentFile=" /etc/systemd/system/gunicorn.service
echo ""

# Solution: Add environment variables directly to gunicorn service
echo "4. Creating updated gunicorn service with explicit environment..."

# Read API_KEY from .env
API_KEY=$(grep "^API_KEY=" /var/www/scan2food/application/scan2food/.env | cut -d= -f2)

if [ -z "$API_KEY" ]; then
    echo "   ✗ ERROR: Could not read API_KEY from .env"
    exit 1
fi

echo "   API_KEY found: ${API_KEY:0:20}..."

# Create service file with explicit Environment directive
sudo tee /etc/systemd/system/gunicorn.service > /dev/null << EOF
[Unit]
Description=Gunicorn daemon
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/scan2food/application/scan2food
Environment="API_KEY=$API_KEY"
Environment="DJANGO_ENV=production"
Environment="LIVE_ORDERS_WS_KEY=05XnhaghUWM6Hd7YVR6_iPcJGfH_YDn3RiDv1Rh-zNM"
Environment="PAYMENT_STATUS_WS_KEY=vy8ALNb9ev6DvTFGHv9IC3RgQ0xL5shqNmnFmDEHNqM"
Environment="CHAT_WS_KEY=A0B9sna1Pdio-1MdXHG8kQJwuC_45Ok2ZmlQbS_0B-U"
EnvironmentFile=/var/www/scan2food/application/scan2food/.env
ExecStart=/var/www/scan2food/application/scan2food/venv/bin/gunicorn --workers 2 --bind unix:/var/www/scan2food/application/scan2food/gunicorn.sock theatreApp.wsgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "   ✓ Updated gunicorn.service with explicit Environment directives"
echo ""

# Reload and restart
echo "5. Reloading systemd and restarting services..."
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
sudo systemctl restart daphne
sleep 3
echo "   ✓ Services restarted"
echo ""

# Test
echo "6. Testing API endpoint (should return 401)..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://scan2food.com/theatre/api/theatre-detail)
echo "   Response code: $HTTP_CODE"

if [ "$HTTP_CODE" = "401" ]; then
    echo "   ✅ SUCCESS! Middleware is now working!"
else
    echo "   ⚠️  Still getting $HTTP_CODE - checking logs..."
    sudo journalctl -u gunicorn -n 20 | grep -E "(MIDDLEWARE|API_KEY|Error)"
fi
echo ""

echo "7. Checking for middleware logs..."
MIDDLEWARE_LOGS=$(sudo journalctl -u gunicorn -n 50 | grep -c "\[MIDDLEWARE\]")
if [ $MIDDLEWARE_LOGS -gt 0 ]; then
    echo "   ✅ Found $MIDDLEWARE_LOGS middleware log entries!"
    sudo journalctl -u gunicorn -n 50 | grep "\[MIDDLEWARE\]" | tail -5
else
    echo "   ⚠️  No middleware logs yet - make a test request"
fi
echo ""

echo "=== FIX COMPLETE ==="
echo ""
echo "Test commands:"
echo "  Without API key: curl -i https://scan2food.com/theatre/api/theatre-detail"
echo "  With API key: curl -i -H 'X-API-Key: $API_KEY' https://scan2food.com/theatre/api/theatre-detail"
