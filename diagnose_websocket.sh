#!/bin/bash

# WebSocket Diagnostic Script
# Run this on the server to diagnose why WebSockets are failing

echo "=========================================="
echo "WEBSOCKET DIAGNOSTIC SCRIPT"
echo "=========================================="
echo ""

# Check if Daphne is running
echo "1. Checking Daphne service status..."
sudo systemctl status daphne --no-pager | head -n 10
echo ""

# Check if .env has WebSocket keys
echo "2. Checking .env file for WebSocket keys..."
if grep -q "LIVE_ORDERS_WS_KEY" /var/www/scan2food/application/scan2food/.env; then
    echo "✓ LIVE_ORDERS_WS_KEY found in .env"
else
    echo "✗ LIVE_ORDERS_WS_KEY NOT found in .env"
fi

if grep -q "PAYMENT_STATUS_WS_KEY" /var/www/scan2food/application/scan2food/.env; then
    echo "✓ PAYMENT_STATUS_WS_KEY found in .env"
else
    echo "✗ PAYMENT_STATUS_WS_KEY NOT found in .env"
fi

if grep -q "CHAT_WS_KEY" /var/www/scan2food/application/scan2food/.env; then
    echo "✓ CHAT_WS_KEY found in .env"
else
    echo "✗ CHAT_WS_KEY NOT found in .env"
fi
echo ""

# Check if static files have API keys
echo "3. Checking if static JavaScript files have API keys..."
if [ -f "/var/www/scan2food/static/theatre_js/live-orders/worker.js" ]; then
    if grep -q "05XnhaghUWM6Hd7YVR6" /var/www/scan2food/static/theatre_js/live-orders/worker.js; then
        echo "✓ API key found in /var/www/scan2food/static/theatre_js/live-orders/worker.js"
    else
        echo "✗ API key NOT found in /var/www/scan2food/static/theatre_js/live-orders/worker.js"
        echo "  This means collectstatic hasn't been run!"
    fi
else
    echo "✗ File /var/www/scan2food/static/theatre_js/live-orders/worker.js does not exist"
fi
echo ""

# Check source files
echo "4. Checking source JavaScript files..."
if grep -q "05XnhaghUWM6Hd7YVR6" /var/www/scan2food/static_files/scan2food-static/static/theatre_js/live-orders/worker.js; then
    echo "✓ API key found in source file (static_files/)"
else
    echo "✗ API key NOT found in source file"
fi
echo ""

# Check Daphne logs for errors
echo "5. Recent Daphne logs (last 20 lines)..."
sudo journalctl -u daphne -n 20 --no-pager
echo ""

echo "=========================================="
echo "DIAGNOSIS COMPLETE"
echo "=========================================="
echo ""
echo "If API key is NOT in /var/www/scan2food/static/, run:"
echo "  cd /var/www/scan2food/application/scan2food"
echo "  source venv/bin/activate"
echo "  python manage.py collectstatic --noinput --clear"
echo "  sudo systemctl restart daphne nginx"
echo ""
