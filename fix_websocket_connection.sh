#!/bin/bash

# Fix WebSocket Connection Issues
# This script updates Redis configuration in Django settings and restarts services

echo "=========================================="
echo "FIXING WEBSOCKET CONNECTION"
echo "=========================================="
echo ""

# Navigate to Django project directory
cd /var/www/scan2food/application/scan2food

# Step 1: Update CHANNEL_LAYERS to include Redis password
echo "Step 1: Updating CHANNEL_LAYERS configuration with Redis password..."

# Backup settings.py
cp theatreApp/settings.py theatreApp/settings.py.backup_$(date +%Y%m%d_%H%M%S)

# Update the CHANNEL_LAYERS configuration to include password
cat > /tmp/channel_layers_config.py << 'EOF'
# CHANNEL_LAYERS - Using Redis for inter-process communication
# This allows Gunicorn workers to send WebSocket updates to Daphne
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis://127.0.0.1:6379/0?password=scann2Food")],
        },
    },
}
EOF

# Find and replace the CHANNEL_LAYERS section
python3 << 'PYTHON_SCRIPT'
import re

# Read the settings file
with open('theatreApp/settings.py', 'r') as f:
    content = f.read()

# Pattern to match the CHANNEL_LAYERS configuration
pattern = r'CHANNEL_LAYERS = \{[^}]*"default": \{[^}]*"BACKEND": "channels_redis\.core\.RedisChannelLayer",[^}]*"CONFIG": \{[^}]*"hosts": \[[^\]]*\],[^}]*\},[^}]*\},[^}]*\}'

# New configuration with password
replacement = '''CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis://127.0.0.1:6379/0?password=scann2Food")],
        },
    },
}'''

# Replace the configuration
new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write back
with open('theatreApp/settings.py', 'w') as f:
    f.write(new_content)

print("✓ CHANNEL_LAYERS configuration updated")
PYTHON_SCRIPT

echo ""

# Step 2: Verify Redis is running and accessible
echo "Step 2: Checking Redis connection..."
redis-cli -a scann2Food PING > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Redis is running and accessible"
else
    echo "✗ Redis connection failed - starting Redis..."
    sudo systemctl start redis
    sleep 2
    redis-cli -a scann2Food PING > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✓ Redis started successfully"
    else
        echo "✗ Redis still not accessible - check Redis configuration"
        exit 1
    fi
fi

echo ""

# Step 3: Check if channels_redis is installed
echo "Step 3: Checking channels_redis package..."
source venv/bin/activate
pip show channels-redis > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ channels-redis is installed"
else
    echo "Installing channels-redis..."
    pip install channels-redis
    echo "✓ channels-redis installed"
fi

echo ""

# Step 4: Restart Daphne service
echo "Step 4: Restarting Daphne (WebSocket server)..."
sudo systemctl restart daphne
sleep 3

# Check if Daphne started successfully
sudo systemctl is-active --quiet daphne
if [ $? -eq 0 ]; then
    echo "✓ Daphne restarted successfully"
else
    echo "✗ Daphne failed to start - checking logs..."
    sudo journalctl -u daphne -n 20 --no-pager
    exit 1
fi

echo ""

# Step 5: Restart Gunicorn service
echo "Step 5: Restarting Gunicorn..."
sudo systemctl restart gunicorn
sleep 2

# Check if Gunicorn started successfully
sudo systemctl is-active --quiet gunicorn
if [ $? -eq 0 ]; then
    echo "✓ Gunicorn restarted successfully"
else
    echo "✗ Gunicorn failed to start - checking logs..."
    sudo journalctl -u gunicorn -n 20 --no-pager
fi

echo ""

# Step 6: Restart Nginx
echo "Step 6: Restarting Nginx..."
sudo systemctl restart nginx
if [ $? -eq 0 ]; then
    echo "✓ Nginx restarted successfully"
else
    echo "✗ Nginx failed to restart"
    exit 1
fi

echo ""
echo "=========================================="
echo "WEBSOCKET FIX COMPLETED"
echo "=========================================="
echo ""
echo "Testing WebSocket endpoints..."
echo ""

# Test WebSocket endpoints
echo "1. Testing /ws/all-seat-datasocket/..."
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: test" https://scan2food.com/ws/all-seat-datasocket/ 2>&1 | head -n 1

echo ""
echo "2. Testing /ws/chat-socket/..."
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: test" https://scan2food.com/ws/chat-socket/ 2>&1 | head -n 1

echo ""
echo "=========================================="
echo "NEXT STEPS:"
echo "=========================================="
echo "1. Open browser and go to: https://scan2food.com/admin-portal/"
echo "2. Check browser console for WebSocket connection status"
echo "3. If still getting errors, check logs:"
echo "   sudo journalctl -u daphne -f"
echo ""
echo "To view real-time WebSocket logs:"
echo "   sudo journalctl -u daphne -f | grep -i websocket"
echo ""
