#!/bin/bash

# Fix WebSocket connection issues on production server
# This checks and restarts the Daphne service

SERVER="165.22.219.111"

echo "============================================================"
echo "Fixing WebSocket Connection on Production"
echo "============================================================"
echo ""

ssh root@$SERVER << 'ENDSSH'

echo "Step 1: Checking Daphne service status..."
systemctl status daphne --no-pager | head -n 10

echo ""
echo "Step 2: Restarting Daphne service..."
systemctl restart daphne

echo ""
echo "Step 3: Checking if Daphne is now running..."
sleep 2
systemctl status daphne --no-pager | head -n 10

echo ""
echo "Step 4: Checking if port 8001 is listening..."
netstat -tlnp | grep 8001 || ss -tlnp | grep 8001

echo ""
echo "Step 5: Checking Daphne logs for errors..."
journalctl -u daphne -n 20 --no-pager

echo ""
echo "============================================================"
echo "WebSocket Fix Completed"
echo "============================================================"

ENDSSH

echo ""
echo "Test the WebSocket connection at:"
echo "https://scan2food.com/theatre/live-orders"
echo ""
