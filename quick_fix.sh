#!/bin/bash
# Quick Fix Script - Run this to verify and fix live orders

echo "=========================================="
echo "LIVE ORDERS QUICK FIX"
echo "=========================================="
echo ""

cd /var/www/scan2food

echo "Step 1: Checking Redis configuration..."
echo ""
python3 verify_redis_working.py
echo ""

read -p "Did you see 'SUCCESS: Using RedisChannelLayer'? (y/n): " redis_ok

if [ "$redis_ok" != "y" ]; then
    echo ""
    echo "Redis not active. Restarting services..."
    sudo systemctl restart redis-server
    sudo systemctl restart gunicorn
    sudo systemctl restart daphne
    echo ""
    echo "Waiting 10 seconds for services to start..."
    sleep 10
    echo ""
    echo "Checking again..."
    python3 verify_redis_working.py
    echo ""
fi

echo ""
echo "Step 2: Testing WebSocket flow..."
echo ""
echo "IMPORTANT: Open live orders page in browser NOW!"
echo "URL: https://calculatentrade.com/live-orders/"
echo ""
read -p "Press Enter when live orders page is open..."

echo ""
echo "Sending test order..."
python3 test_websocket_flow.py
echo ""

read -p "Did test order appear on live orders page? (y/n): " test_ok

if [ "$test_ok" = "y" ]; then
    echo ""
    echo "=========================================="
    echo "✅ SUCCESS! Live orders are working!"
    echo "=========================================="
    echo ""
    echo "Now create a real order and it should appear instantly."
    echo ""
else
    echo ""
    echo "=========================================="
    echo "❌ Test order did not appear"
    echo "=========================================="
    echo ""
    echo "Checking services..."
    echo ""
    
    echo "Redis status:"
    sudo systemctl status redis-server --no-pager | head -5
    echo ""
    
    echo "Daphne status:"
    sudo systemctl status daphne --no-pager | head -5
    echo ""
    
    echo "Gunicorn status:"
    sudo systemctl status gunicorn --no-pager | head -5
    echo ""
    
    echo "Recent Daphne logs:"
    sudo journalctl -u daphne -n 20 --no-pager
    echo ""
    
    echo "=========================================="
    echo "NEXT STEPS:"
    echo "=========================================="
    echo ""
    echo "1. Check browser console (F12) for WebSocket errors"
    echo "2. Run full diagnostic: ./diagnose_redis_websocket.sh"
    echo "3. Send diagnostic output to developer"
    echo ""
fi

echo "=========================================="
