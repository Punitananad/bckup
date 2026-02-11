#!/bin/bash

echo "=========================================="
echo "CRITICAL WEBSOCKET FIXES"
echo "=========================================="
echo ""

# Step 1: Check current nginx static path
echo "Step 1: Checking nginx static path..."
echo "Current nginx config:"
grep -A 5 "location /static" /etc/nginx/sites-available/scan2food

echo ""
echo "Django STATIC_ROOT is: /var/www/scan2food/static"
echo ""
read -p "Does nginx point to /var/www/scan2food/staticfiles? (y/n): " nginx_wrong

if [ "$nginx_wrong" = "y" ]; then
    echo ""
    echo "FIXING: Updating nginx to point to correct static path..."
    sudo sed -i 's|alias /var/www/scan2food/staticfiles/;|alias /var/www/scan2food/static/;|g' /etc/nginx/sites-available/scan2food
    
    echo "Verifying change..."
    grep -A 5 "location /static" /etc/nginx/sites-available/scan2food
    
    echo ""
    echo "Restarting nginx..."
    sudo systemctl restart nginx
    
    echo ""
    echo "Testing if static files now have API key..."
    curl -s https://calculatentrade.com/static/theatre_js/live-orders/worker.js | grep -o "05XnhaghUWM6Hd7YVR6" | head -1
    
    if [ $? -eq 0 ]; then
        echo "✅ SUCCESS: API key found in served static file!"
    else
        echo "❌ FAILED: API key still not in served file"
    fi
fi

echo ""
echo "=========================================="
echo "Step 2: Check WebSocket connection"
echo "=========================================="
echo ""
echo "Checking Daphne logs for WSREJECT..."
sudo journalctl -u daphne -n 50 --no-pager | grep -E "WSREJECT|WSCONNECT|WebSocket" | tail -20

echo ""
echo "=========================================="
echo "Step 3: Test WebSocket with API key"
echo "=========================================="
echo ""
echo "You need to:"
echo "1. Open browser DevTools (F12)"
echo "2. Go to: https://calculatentrade.com/theatre/live-orders/"
echo "3. Do HARD REFRESH: Ctrl+Shift+R"
echo "4. Check Network tab -> WS filter"
echo "5. Look for WebSocket URL - should include ?key=..."
echo ""
echo "Expected URL:"
echo "wss://calculatentrade.com/ws/all-seat-datasocket/?key=05XnhaghUWM6Hd7YVR6_iPcJGfH_YDn3RiDv1Rh-zNM"
echo ""
read -p "Press Enter when ready to check logs..."

echo ""
echo "Recent WebSocket connection attempts:"
sudo journalctl -u daphne -n 20 --no-pager | grep -E "WSREJECT|WSCONNECT"

echo ""
echo "=========================================="
echo "DIAGNOSIS COMPLETE"
echo "=========================================="
