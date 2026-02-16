#!/bin/bash

# Clear Menu Cache from Redis
# This will force all menu data to be regenerated

echo "=========================================="
echo "CLEARING MENU CACHE"
echo "=========================================="
echo ""

# Clear all theatre_menu_* keys from Redis
echo "Clearing Redis cache for menu data..."
redis-cli -a scann2Food --scan --pattern "theatre_menu_*" | xargs -L 1 redis-cli -a scann2Food DEL

echo "✓ Redis menu cache cleared"
echo ""

# Restart services to ensure clean state
echo "Restarting services..."
sudo systemctl restart daphne
sudo systemctl restart gunicorn

echo "✓ Services restarted"
echo ""

echo "=========================================="
echo "CACHE CLEARED SUCCESSFULLY"
echo "=========================================="
echo ""
echo "Users should now:"
echo "1. Clear their browser cache (Ctrl+Shift+Delete)"
echo "2. Or use Ctrl+F5 to hard refresh the page"
echo "3. Or wait for browser cache to expire"
echo ""
echo "New visitors will see menu immediately without issues."
