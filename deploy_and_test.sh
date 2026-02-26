#!/bin/bash

# Deployment and Testing Script for Scan2Food
SERVER="165.22.219.111"

echo "============================================================"
echo "Deploying and Testing All Orders Fix"
echo "============================================================"
echo ""

ssh root@$SERVER << 'ENDSSH'

cd /var/www/scan2food

echo "Step 1: Pulling latest code..."
git stash
git pull origin main

echo ""
echo "Step 2: Clearing Python cache..."
find . -name "*.pyc" -delete
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true

echo ""
echo "Step 3: Restarting services..."
systemctl restart gunicorn
systemctl restart daphne

echo ""
echo "Step 4: Waiting for services to start..."
sleep 3

echo ""
echo "Step 5: Checking service status..."
systemctl status gunicorn --no-pager -l | head -n 15
systemctl status daphne --no-pager -l | head -n 15

echo ""
echo "Step 6: Testing SSE endpoint directly..."
timeout 5 curl -N -H "Cookie: sessionid=test" \
  "http://localhost:8000/theatre/api/all-orders-sse?daterange=&order-status=Success&selected-theatre=" \
  2>&1 | head -n 20

echo ""
echo "Step 7: Checking recent gunicorn logs for errors..."
journalctl -u gunicorn -n 30 --no-pager | grep -i "error\|exception\|traceback" || echo "No errors found"

echo ""
echo "Step 8: Checking recent daphne logs for errors..."
journalctl -u daphne -n 30 --no-pager | grep -i "error\|exception\|traceback" || echo "No errors found"

echo ""
echo "============================================================"
echo "Deployment Complete"
echo "============================================================"

ENDSSH

echo ""
echo "Now test at: https://scan2food.com/admin-portal/all-orders"
echo ""
