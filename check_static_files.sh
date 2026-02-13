#!/bin/bash

echo "=== Checking Static Files ==="
echo ""

echo "1. Check file on disk:"
grep "ws_key" /var/www/scan2food/static/theatre_js/live-orders/worker.js | head -1
echo ""

echo "2. Check what Nginx serves:"
curl -s https://calculatentrade.com/static/theatre_js/live-orders/worker.js | grep "ws_key" | head -1
echo ""

echo "3. Check Nginx config:"
grep -A 5 "location /static/" /etc/nginx/sites-available/scan2food
echo ""

echo "4. Check if both paths exist:"
ls -la /var/www/scan2food/static/theatre_js/live-orders/worker.js 2>/dev/null && echo "✓ /static exists"
ls -la /var/www/scan2food/staticfiles/theatre_js/live-orders/worker.js 2>/dev/null && echo "✓ /staticfiles exists"
