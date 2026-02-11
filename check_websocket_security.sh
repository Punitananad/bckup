#!/bin/bash

echo "=== WebSocket Security Diagnostic ==="
echo ""

echo "1. Checking if .env file exists and has WebSocket keys:"
if [ -f "/var/www/scan2food/application/scan2food/.env" ]; then
    echo "✓ .env file exists"
    echo ""
    echo "WebSocket keys in .env:"
    grep -E "LIVE_ORDERS_WS_KEY|PAYMENT_STATUS_WS_KEY|CHAT_WS_KEY" /var/www/scan2food/application/scan2food/.env || echo "✗ No WebSocket keys found in .env"
else
    echo "✗ .env file not found"
fi

echo ""
echo "2. Checking latest git commit:"
cd /var/www/scan2food
git log -1 --oneline

echo ""
echo "3. Checking if consumer files have security checks:"
echo ""
echo "allSeatConsumer.py:"
grep -A 2 "LIVE_ORDERS_WS_KEY" /var/www/scan2food/application/scan2food/theatre/consumers/allSeatConsumer.py || echo "✗ Security check not found"

echo ""
echo "paymentSocket.py:"
grep -A 2 "PAYMENT_STATUS_WS_KEY" /var/www/scan2food/application/scan2food/theatre/consumers/paymentSocket.py || echo "✗ Security check not found"

echo ""
echo "chatConsumer.py:"
grep -A 2 "CHAT_WS_KEY" /var/www/scan2food/application/scan2food/chat_box/consumer/chatConsumer.py || echo "✗ Security check not found"

echo ""
echo "4. Checking Daphne service status:"
sudo systemctl status daphne --no-pager | head -20

echo ""
echo "5. Checking Daphne logs for errors:"
sudo journalctl -u daphne -n 50 --no-pager | grep -i "error\|exception\|failed" | tail -10

echo ""
echo "6. Testing WebSocket connection (should fail without key):"
timeout 3 wscat -c "wss://calculatentrade.com/ws/all-seat-datasocket/" 2>&1 || echo "Connection test completed"

echo ""
echo "=== Diagnostic Complete ==="
