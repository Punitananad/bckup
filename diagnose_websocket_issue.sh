#!/bin/bash
# Diagnose Live Orders WebSocket Issue

echo "=========================================="
echo "LIVE ORDERS WEBSOCKET DIAGNOSTIC"
echo "=========================================="
echo ""

# 1. Check if Daphne is running
echo "1. Checking Daphne Status:"
sudo systemctl status daphne --no-pager | grep -E "Active|Memory|Tasks"
echo ""

# 2. Check WebSocket connections
echo "2. Active WebSocket Connections:"
sudo ss -tn | grep :8001 | wc -l
echo "connections to port 8001"
echo ""

# 3. Check Daphne logs for WebSocket activity
echo "3. Recent Daphne Logs (last 20 lines):"
sudo journalctl -u daphne -n 20 --no-pager
echo ""

# 4. Check if channel layer is working
echo "4. Testing Channel Layer:"
cd /var/www/scan2food/application/scan2food
source venv/bin/activate
python3 << 'EOF'
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theatreApp.settings')
django.setup()

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

channel_layer = get_channel_layer()
print(f"Channel Layer Backend: {channel_layer.__class__.__name__}")
print(f"Channel Layer Config: {channel_layer}")

# Test sending a message
try:
    async_to_sync(channel_layer.group_send)(
        'all-seat-status',
        {
            'type': 'table_data',
            'updated_table_data': json.dumps({
                'msg_typ': 'test',
                'message': 'Test message from diagnostic script'
            })
        }
    )
    print("✅ Successfully sent test message to channel layer")
except Exception as e:
    print(f"❌ Error sending message: {e}")
EOF
echo ""

# 5. Check for errors in Gunicorn logs
echo "5. Recent Gunicorn Errors:"
sudo journalctl -u gunicorn -n 20 --no-pager | grep -i error
echo ""

# 6. Check Django settings for CHANNEL_LAYERS
echo "6. Channel Layers Configuration:"
cd /var/www/scan2food/application/scan2food
grep -A 5 "CHANNEL_LAYERS" theatreApp/settings.py
echo ""

# 7. Check if InMemoryChannelLayer is working
echo "7. Checking InMemoryChannelLayer:"
python3 << 'EOF'
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theatreApp.settings')
django.setup()

from django.conf import settings
print(f"CHANNEL_LAYERS config: {settings.CHANNEL_LAYERS}")
EOF
echo ""

# 8. Test WebSocket endpoint
echo "8. Testing WebSocket Endpoint:"
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
  https://calculatentrade.com/ws/all-seat-datasocket/ 2>&1 | head -20
echo ""

echo "=========================================="
echo "DIAGNOSTIC COMPLETE"
echo "=========================================="
echo ""
echo "COMMON ISSUES:"
echo "1. If channel layer shows 'InMemoryChannelLayer' but messages aren't received:"
echo "   - InMemoryChannelLayer only works within same process"
echo "   - Gunicorn workers can't communicate with Daphne"
echo "   - Solution: Use Redis for channel layer"
echo ""
echo "2. If WebSocket connects but no updates:"
echo "   - Check if update_websocket() is being called"
echo "   - Check Daphne logs for errors"
echo "   - Verify channel layer is configured correctly"
echo ""
echo "3. If 'upstream prematurely closed' errors:"
echo "   - Workers are being killed due to memory"
echo "   - Already fixed by reducing workers to 2"
