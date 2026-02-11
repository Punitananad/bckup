#!/bin/bash

# Quick deployment script - run this on the server
# This fixes the WebSocket security caching issue

echo "=========================================="
echo "WEBSOCKET SECURITY FIX DEPLOYMENT"
echo "=========================================="
echo ""

# Pull latest code
cd /var/www/scan2food
echo "Pulling latest code..."
git pull origin main
echo ""

# Navigate to Django directory
cd application/scan2food
source venv/bin/activate

# Remove old static files
echo "Removing old static files..."
rm -rf /var/www/scan2food/static/theatre_js/live-orders/
rm -rf /var/www/scan2food/static/theatre_js/chat-box/
rm -rf /var/www/scan2food/static/theatre_js/all-seat-socket.js
rm -rf /var/www/scan2food/static/theatre_js/payment-socket.js
rm -rf /var/www/scan2food/static/dashboard/
rm -rf /var/www/scan2food/static/chatBox/
echo "✓ Done"
echo ""

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear
echo "✓ Done"
echo ""

# Restart services
echo "Restarting services..."
sudo systemctl restart gunicorn
sudo systemctl restart daphne
sudo systemctl restart nginx
echo "✓ Done"
echo ""

# Verify
echo "Verifying deployment..."
if grep -q "05XnhaghUWM6Hd7YVR6" /var/www/scan2food/static/theatre_js/live-orders/worker.js; then
    echo "✓ API key found in static files - DEPLOYMENT SUCCESSFUL!"
else
    echo "✗ API key NOT found - DEPLOYMENT FAILED!"
    exit 1
fi
echo ""

echo "=========================================="
echo "DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "IMPORTANT: Tell users to do HARD REFRESH (Ctrl+Shift+R)"
echo ""
echo "To monitor WebSocket connections:"
echo "  sudo journalctl -u daphne -f"
echo ""
echo "Look for 'WSCONNECT' messages (not 'WSREJECT')"
echo ""
