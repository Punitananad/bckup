#!/usr/bin/env python3
"""
Quick diagnostic to verify Redis channel layer is working
Run this on the server: python3 verify_redis_working.py
"""

import django
import os
import sys

# Setup Django
sys.path.insert(0, '/var/www/scan2food/application/scan2food')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theatreApp.settings')
django.setup()

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

print("=" * 60)
print("REDIS CHANNEL LAYER VERIFICATION")
print("=" * 60)
print()

# Get channel layer
channel_layer = get_channel_layer()

print(f"✓ Channel Layer Backend: {channel_layer.__class__.__name__}")
print(f"✓ Channel Layer Type: {type(channel_layer)}")
print()

# Check if it's Redis
if "Redis" in channel_layer.__class__.__name__:
    print("✅ SUCCESS: Using RedisChannelLayer")
    print("   Redis is properly configured for WebSocket communication")
    print()
    
    # Test sending a message
    print("Testing message send to 'all-seat-status' group...")
    try:
        async_to_sync(channel_layer.group_send)(
            'all-seat-status',
            {
                'type': 'table_data',
                'updated_table_data': json.dumps({
                    'msg_typ': 'test',
                    'message': 'Diagnostic test from verify_redis_working.py',
                    'seat_id': 999,
                    'theatre_id': 31
                })
            }
        )
        print("✅ Message sent successfully!")
        print()
        print("RESULT: Redis channel layer is working correctly!")
        print()
        print("If live orders still don't work, check:")
        print("1. Browser console (F12) for WebSocket errors")
        print("2. Daphne logs: sudo journalctl -u daphne -f")
        print("3. Make sure WebSocket is connected (check browser Network tab)")
        
    except Exception as e:
        print(f"❌ ERROR sending message: {e}")
        print()
        print("This means Redis is configured but not working properly.")
        print("Check:")
        print("1. Redis is running: sudo systemctl status redis-server")
        print("2. Redis is accessible: redis-cli ping")
        print("3. Restart services: sudo systemctl restart gunicorn daphne")
        import traceback
        traceback.print_exc()
        
else:
    print("❌ PROBLEM: Still using InMemoryChannelLayer")
    print("   This will NOT work for live orders!")
    print()
    print("Fix:")
    print("1. Make sure settings.py has RedisChannelLayer configured")
    print("2. Restart services: sudo systemctl restart gunicorn daphne")
    print("3. Run this script again")

print()
print("=" * 60)
