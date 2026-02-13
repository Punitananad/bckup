#!/bin/bash

# CRITICAL WEBSOCKET FIXES
# Run this on the server: bash CRITICAL_FIXES_RUN_NOW.sh

set -e  # Exit on any error

echo "=========================================="
echo "CRITICAL FIX 1: Nginx Static Path"
echo "=========================================="

# Backup nginx config first
sudo cp /etc/nginx/sites-available/scan2food /etc/nginx/sites-available/scan2food.backup.$(date +%Y%m%d_%H%M%S)

# Fix the static path mismatch
echo "Fixing Nginx static path from 'staticfiles' to 'static'..."
sudo sed -i 's|/var/www/scan2food/staticfiles/|/var/www/scan2food/static/|g' /etc/nginx/sites-available/scan2food

# Test nginx config
echo "Testing Nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✓ Nginx config is valid"
    sudo systemctl restart nginx
    echo "✓ Nginx restarted"
else
    echo "❌ Nginx config has errors - restoring backup"
    sudo cp /etc/nginx/sites-available/scan2food.backup.* /etc/nginx/sites-available/scan2food
    exit 1
fi

echo ""
echo "=========================================="
echo "CRITICAL FIX 2: Clear Browser Cache Headers"
echo "=========================================="

# Add no-cache headers for JS files to prevent browser caching
echo "Adding cache-control headers for JavaScript files..."

# Check if the location block for JS files exists
if ! grep -q "location ~* \.js$" /etc/nginx/sites-available/scan2food; then
    echo "Adding JS cache control to Nginx config..."
    
    # This will add the JS cache control before the closing brace of the server block
    sudo sed -i '/location \/static\/ {/a\    \n    # Prevent caching of JavaScript files\n    location ~* \\.js$ {\n        add_header Cache-Control "no-cache, no-store, must-revalidate";\n        add_header Pragma "no-cache";\n        add_header Expires "0";\n    }' /etc/nginx/sites-available/scan2food
    
    sudo nginx -t && sudo systemctl restart nginx
    echo "✓ Cache headers added"
else
    echo "✓ JS cache control already exists"
fi

echo ""
echo "=========================================="
echo "VERIFICATION"
echo "=========================================="

echo ""
echo "1. Checking if API key is in static file on disk:"
if grep -q "05XnhaghUWM6Hd7YVR6" /var/www/scan2food/static/theatre_js/live-orders/worker.js; then
    echo "   ✓ API key found in file"
else
    echo "   ❌ API key NOT in file - need to run collectstatic"
fi

echo ""
echo "2. Checking what Nginx serves (first 30 lines):"
curl -s https://calculatentrade.com/static/theatre_js/live-orders/worker.js | head -30

echo ""
echo "3. Checking for API key in served file:"
if curl -s https://calculatentrade.com/static/theatre_js/live-orders/worker.js | grep -q "05XnhaghUWM6Hd7YVR6"; then
    echo "   ✓ API key is being served by Nginx"
else
    echo "   ❌ API key NOT in served file"
fi

echo ""
echo "=========================================="
echo "NEXT STEPS"
echo "=========================================="
echo ""
echo "1. Users must do HARD REFRESH in browser:"
echo "   - Chrome/Firefox: Ctrl + Shift + R"
echo "   - Safari: Cmd + Shift + R"
echo ""
echo "2. Check browser console - WebSocket URL should be:"
echo "   wss://calculatentrade.com/ws/all-seat-datasocket/?key=05XnhaghUWM6Hd7YVR6_iPcJGfH_YDn3RiDv1Rh-zNM"
echo ""
echo "3. Monitor Daphne logs:"
echo "   sudo journalctl -u daphne -f"
echo ""
echo "   Should see 'WSCONNECT' instead of 'WSREJECT'"
echo ""
