#!/bin/bash

echo "=========================================="
echo "FIXING NGINX STATIC PATH MISMATCH"
echo "=========================================="
echo ""

# Backup current config
echo "Creating backup..."
sudo cp /etc/nginx/sites-available/scan2food /etc/nginx/sites-available/scan2food.backup.$(date +%Y%m%d_%H%M%S)

# Show current config
echo ""
echo "CURRENT nginx config:"
echo "---"
sudo grep -A 5 "location /static" /etc/nginx/sites-available/scan2food
echo "---"

# Fix the path
echo ""
echo "FIXING: Changing staticfiles/ to static/..."
sudo sed -i 's|/var/www/scan2food/staticfiles/|/var/www/scan2food/static/|g' /etc/nginx/sites-available/scan2food

# Show new config
echo ""
echo "NEW nginx config:"
echo "---"
sudo grep -A 5 "location /static" /etc/nginx/sites-available/scan2food
echo "---"

# Test nginx config
echo ""
echo "Testing nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx config is valid"
    
    # Restart nginx
    echo ""
    echo "Restarting nginx..."
    sudo systemctl restart nginx
    
    echo "✅ Nginx restarted"
    
    # Test if static files now work
    echo ""
    echo "=========================================="
    echo "TESTING STATIC FILE DELIVERY"
    echo "=========================================="
    echo ""
    
    echo "Testing if API key is now in served JavaScript..."
    RESULT=$(curl -s https://calculatentrade.com/static/theatre_js/live-orders/worker.js | grep -o "05XnhaghUWM6Hd7YVR6" | head -1)
    
    if [ -n "$RESULT" ]; then
        echo "✅ SUCCESS! API key found in served file!"
        echo "   Found: $RESULT"
    else
        echo "❌ FAILED: API key still not found"
        echo ""
        echo "Checking what nginx is actually serving..."
        curl -s https://calculatentrade.com/static/theatre_js/live-orders/worker.js | head -20
    fi
    
    echo ""
    echo "=========================================="
    echo "NEXT STEPS"
    echo "=========================================="
    echo ""
    echo "1. Open browser: https://calculatentrade.com/theatre/live-orders/"
    echo "2. Do HARD REFRESH: Ctrl+Shift+R (or Cmd+Shift+R on Mac)"
    echo "3. Open DevTools (F12)"
    echo "4. Go to Network tab → Filter by 'WS'"
    echo "5. Check WebSocket URL - should include ?key=..."
    echo ""
    echo "Expected URL:"
    echo "wss://calculatentrade.com/ws/all-seat-datasocket/?key=05XnhaghUWM6Hd7YVR6_iPcJGfH_YDn3RiDv1Rh-zNM"
    echo ""
    echo "Then check Daphne logs:"
    echo "sudo journalctl -u daphne -n 20 --no-pager | grep -E 'WSREJECT|WSCONNECT'"
    
else
    echo "❌ Nginx config has errors!"
    echo "Restoring backup..."
    sudo cp /etc/nginx/sites-available/scan2food.backup.* /etc/nginx/sites-available/scan2food
fi

echo ""
echo "=========================================="
echo "DONE"
echo "=========================================="
