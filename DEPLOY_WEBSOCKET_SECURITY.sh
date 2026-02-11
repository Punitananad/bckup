#!/bin/bash

# WebSocket Security Deployment Script
# This script deploys the WebSocket API key security fix

echo "=========================================="
echo "DEPLOYING WEBSOCKET SECURITY FIX"
echo "=========================================="
echo ""

# Navigate to project directory
cd /var/www/scan2food/application/scan2food || exit 1

# Activate virtual environment
source venv/bin/activate

echo "1. Pulling latest code from GitHub..."
cd /var/www/scan2food
git pull origin main
echo "✓ Code pulled"
echo ""

# Navigate back to Django directory
cd /var/www/scan2food/application/scan2food

echo "2. Removing old static files..."
rm -rf /var/www/scan2food/static/theatre_js/live-orders/
rm -rf /var/www/scan2food/static/theatre_js/chat-box/
rm -rf /var/www/scan2food/static/theatre_js/all-seat-socket.js
rm -rf /var/www/scan2food/static/theatre_js/payment-socket.js
rm -rf /var/www/scan2food/static/dashboard/live-order.js
rm -rf /var/www/scan2food/static/dashboard/chat-box/
rm -rf /var/www/scan2food/static/dashboard/profile/
rm -rf /var/www/scan2food/static/chatBox/
echo "✓ Old static files removed"
echo ""

echo "3. Collecting static files..."
python manage.py collectstatic --noinput --clear
echo "✓ Static files collected"
echo ""

echo "4. Restarting services..."
sudo systemctl restart gunicorn
sudo systemctl restart daphne
sudo systemctl restart nginx
echo "✓ Services restarted"
echo ""

echo "5. Checking service status..."
echo ""
echo "Gunicorn status:"
sudo systemctl status gunicorn --no-pager | head -n 5
echo ""
echo "Daphne status:"
sudo systemctl status daphne --no-pager | head -n 5
echo ""
echo "Nginx status:"
sudo systemctl status nginx --no-pager | head -n 5
echo ""

echo "6. Verifying API key in static files..."
if grep -q "05XnhaghUWM6Hd7YVR6" /var/www/scan2food/static/theatre_js/live-orders/worker.js; then
    echo "✓ API key found in worker.js"
else
    echo "✗ API key NOT found in worker.js - DEPLOYMENT FAILED!"
    exit 1
fi
echo ""

echo "=========================================="
echo "DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "IMPORTANT: Users must do a HARD REFRESH (Ctrl+Shift+R) to clear browser cache"
echo ""
echo "To verify WebSocket connections are working:"
echo "  sudo journalctl -u daphne -f"
echo ""
echo "Look for 'WSCONNECT' messages instead of 'WSREJECT'"
echo ""
