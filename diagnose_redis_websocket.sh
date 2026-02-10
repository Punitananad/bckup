#!/bin/bash
# Comprehensive WebSocket + Redis Diagnostic

echo "=========================================="
echo "WEBSOCKET + REDIS DIAGNOSTIC"
echo "=========================================="
echo ""

cd /var/www/scan2food/application/scan2food
source venv/bin/activate

# 1. Test Redis connection
echo "1. Testing Redis Connection:"
redis-cli ping
echo ""

# 2. Check Channel Layer Configuration
echo "2. Checking Django Channel Layer:"
python3 << 'EOF'
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theatreApp.settings')
django.setup()

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

channel_layer = get_channel_layer()
print(f"Backend: {channel_layer.__class__.__name__}")
print(f"Config: {channel_layer}")

# Test sending a message
try:
    print("\nTesting message send...")
    async_to_sync(channel_layer.group_send)(
        'all-seat-status',
        {
            'type': 'table_data',
            'updated_table_data': json.dumps({
                'msg_typ': 'test',
                'message': 'Diagnostic test message',
                'seat_id': 999,
                'theatre_id': 31
            })
        }
    )
    print("✅ Message sent successfully to channel layer!")
except Exception as e:
    print(f"❌ Error sending message: {e}")
    import traceback
    traceback.print_exc()
EOF
echo ""

# 3. Check Daphne logs for errors
echo "3. Recent Daphne Logs (last 30 lines):"
sudo journalctl -u daphne -n 30 --no-pager
echo ""

# 4. Check Gunicorn logs
echo "4. Recent Gunicorn Logs (last 20 lines):"
sudo journalctl -u gunicorn -n 20 --no-pager
echo ""

# 5. Check Redis logs
echo "5. Redis Status:"
sudo systemctl status redis-server --no-pager | head -20
echo ""

# 6. Monitor Redis activity
echo "6. Monitoring Redis (5 seconds):"
echo "Watching for channel layer activity..."
timeout 5 redis-cli MONITOR || echo "Redis monitor timed out"
echo ""

echo "=========================================="
echo "DIAGNOSTIC COMPLETE"
echo "=========================================="
echo ""
echo "If you see 'RedisChannelLayer' above, Redis is configured correctly."
echo "If message send succeeded, the channel layer is working."
echo ""
echo "Next: Check browser console for WebSocket errors"
echo "Press F12 in browser → Console tab → Look for WebSocket errors"
