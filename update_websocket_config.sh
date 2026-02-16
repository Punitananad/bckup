#!/bin/bash

# Quick WebSocket Fix Script
# Updates CHANNEL_LAYERS configuration with Redis password

echo "Updating WebSocket configuration..."

cd /var/www/scan2food/application/scan2food

# Backup settings
cp theatreApp/settings.py theatreApp/settings.py.backup_ws_$(date +%Y%m%d_%H%M%S)

# Update CHANNEL_LAYERS using sed
sed -i 's|"hosts": \[\("127.0.0.1", 6379\)\]|"hosts": ["redis://:scann2Food@127.0.0.1:6379/0"]|g' theatreApp/settings.py

echo "✓ Configuration updated"

# Verify the change
echo ""
echo "New configuration:"
grep -A 5 "CHANNEL_LAYERS" theatreApp/settings.py | head -n 8

echo ""
echo "Restarting services..."

# Restart services
sudo systemctl restart daphne
sleep 2
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo ""
echo "✓ Services restarted"
echo ""
echo "Testing WebSocket connection..."

# Test WebSocket
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: test" https://scan2food.com/ws/all-seat-datasocket/ 2>&1 | head -n 1

echo ""
echo "Done! Check browser console at https://scan2food.com/admin-portal/"
