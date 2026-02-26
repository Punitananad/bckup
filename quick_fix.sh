#!/bin/bash

SERVER="165.22.219.111"

echo "Restarting Daphne (ASGI server for SSE)..."

ssh root@$SERVER << 'ENDSSH'

cd /var/www/scan2food

echo "Pulling latest code..."
git stash
git pull origin main

echo "Clearing Python cache..."
find . -name "*.pyc" -delete

echo "Restarting Daphne (handles async/SSE requests)..."
systemctl restart daphne

echo "Checking Daphne status..."
systemctl status daphne --no-pager | head -n 15

echo ""
echo "Checking for errors in Daphne logs..."
journalctl -u daphne -n 50 --no-pager

ENDSSH

echo ""
echo "Done! Test at: https://scan2food.com/admin-portal/all-orders"
