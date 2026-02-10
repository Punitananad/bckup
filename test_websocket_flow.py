#!/usr/bin/env python3
"""
Test WebSocket Flow - Simulates sending an order update
Run this on server to test if Redis → Daphne → WebSocket flow works
"""

import django
import os
import sys
import json

# Setup Django
sys.path.insert(0, '/var/www/scan2food/application/scan2food')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theatreApp.settings')
django.setup()

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

print("=" * 70)
print("TESTING WEBSOCKET MESSAGE FLOW")
print("=" * 70)
print()

# Get channel layer
channel_layer = get_channel_layer()

print(f"Channel Layer: {channel_layer.__class__.__name__}")
print()

if "Redis" not in channel_layer.__class__.__name__:
    print("❌ ERROR: Not using RedisChannelLayer!")
    print("   Live orders will NOT work with InMemoryChannelLayer")
    print()
    print("Fix: Update settings.py and restart services")
    sys.exit(1)

print("✅ Using RedisChannelLayer")
print()

# Simulate sending a test order update
print("Sending test order update to 'all-seat-status' group...")
print()

test_order = {
    'theatre_id': 31,
    'seat_id': 999,
    'seat_name': 'Test Hall | Test Seat',
    'theatre_name': 'Test Theatre',
    'order_id': 'TEST-12345',
    'amount': 100,
    'payment_method': 'Online',
    'payment_status': 'Success',
    'msg_typ': 'confirmation',
    'max_time': 30,
    'is_vacent': False,
    'payment_panding': False,
    'type': 'bg-success',
    'message': 'Test order from test_websocket_flow.py',
    'customer-phone': '9999999999',
    'customer-message': '',
    'notification_numbers': '',
    'group': 'all-seat-status'
}

print("Test Order Data:")
print(json.dumps(test_order, indent=2))
print()

try:
    # Send message to channel layer (same as update_websocket() does)
    async_to_sync(channel_layer.group_send)(
        'all-seat-status',
        {
            'type': 'table_data',
            'updated_table_data': json.dumps(test_order)
        }
    )
    
    print("✅ Message sent successfully to Redis!")
    print()
    print("=" * 70)
    print("WHAT TO DO NEXT:")
    print("=" * 70)
    print()
    print("1. Open live orders page in browser:")
    print("   https://calculatentrade.com/live-orders/")
    print()
    print("2. Check if test order appears (Theatre ID: 31, Seat ID: 999)")
    print()
    print("3. If order appears:")
    print("   ✅ WebSocket flow is working!")
    print("   ✅ Redis → Daphne → Browser communication is OK")
    print()
    print("4. If order does NOT appear:")
    print("   ❌ Check browser console (F12) for WebSocket errors")
    print("   ❌ Check Daphne logs: sudo journalctl -u daphne -f")
    print("   ❌ Verify WebSocket is connected in browser")
    print()
    print("5. Monitor Daphne logs while running this script:")
    print("   sudo journalctl -u daphne -f")
    print("   You should see the message being processed")
    print()
    
except Exception as e:
    print(f"❌ ERROR sending message: {e}")
    print()
    print("This means Redis is not working properly.")
    print()
    print("Check:")
    print("1. Redis is running: sudo systemctl status redis-server")
    print("2. Redis is accessible: redis-cli ping")
    print("3. Daphne is running: sudo systemctl status daphne")
    print("4. Restart services: sudo systemctl restart gunicorn daphne redis-server")
    print()
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("=" * 70)
