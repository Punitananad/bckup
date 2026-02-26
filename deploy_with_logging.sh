#!/bin/bash
# Deploy with comprehensive logging enabled

cd /var/www/scan2food

echo "=== Pulling latest code ==="
git pull origin main

echo ""
echo "=== Restarting Gunicorn ==="
systemctl restart gunicorn

echo ""
echo "=== Waiting 3 seconds for Gunicorn to start ==="
sleep 3

echo ""
echo "=== Testing SSE endpoint ==="
curl -N "http://localhost/theatre/api/all-orders-sse?daterange=&order-status=Success&selected-theatre=" 2>&1 | head -n 10

echo ""
echo ""
echo "=== Checking Gunicorn logs for SSE activity ==="
echo "Run this command to see the logs:"
echo "journalctl -u gunicorn -n 100 --no-pager | grep -E '\[SSE\]|\[get_all_orders\]'"
echo ""
echo "Or follow live logs:"
echo "journalctl -u gunicorn -f | grep -E '\[SSE\]|\[get_all_orders\]'"
