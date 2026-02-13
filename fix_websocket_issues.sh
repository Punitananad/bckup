#!/bin/bash

echo "=========================================="
echo "WebSocket Issues Diagnostic & Fix Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}ISSUE 1: Checking Nginx Static Path Configuration${NC}"
echo "Django STATIC_ROOT: /var/www/scan2food/static"
echo "Checking Nginx configuration..."
echo ""

if grep -q "staticfiles" /etc/nginx/sites-available/scan2food; then
    echo -e "${RED}❌ FOUND MISMATCH!${NC}"
    echo "Nginx is configured to serve from 'staticfiles' but Django uses 'static'"
    echo ""
    echo "Current Nginx config:"
    grep -A 2 "location /static" /etc/nginx/sites-available/scan2food
    echo ""
    echo -e "${YELLOW}FIX REQUIRED:${NC}"
    echo "Run this command to fix:"
    echo "sudo sed -i 's|/var/www/scan2food/staticfiles/|/var/www/scan2food/static/|g' /etc/nginx/sites-available/scan2food"
    echo "sudo systemctl restart nginx"
else
    echo -e "${GREEN}✓ Nginx static path looks correct${NC}"
fi

echo ""
echo -e "${YELLOW}ISSUE 2: Checking if API keys are in static files${NC}"
echo "Checking worker.js for API key..."

if grep -q "05XnhaghUWM6Hd7YVR6" /var/www/scan2food/static/theatre_js/live-orders/worker.js 2>/dev/null; then
    echo -e "${GREEN}✓ API key found in static file on disk${NC}"
else
    echo -e "${RED}❌ API key NOT found in static file${NC}"
    echo "Run: cd /var/www/scan2food/application/scan2food && python manage.py collectstatic --noinput --clear"
fi

echo ""
echo -e "${YELLOW}ISSUE 3: Testing what Nginx actually serves${NC}"
echo "Fetching from live server..."
curl -s https://calculatentrade.com/static/theatre_js/live-orders/worker.js | head -20

echo ""
echo ""
echo -e "${YELLOW}ISSUE 4: Consumer Connection Logic${NC}"
echo "Checking consumer code for proper lifecycle..."

if grep -q "await self.close()" /var/www/scan2food/application/scan2food/theatre/consumers/allSeatConsumer.py; then
    echo -e "${GREEN}✓ Consumer has key validation${NC}"
else
    echo -e "${RED}❌ Consumer missing key validation${NC}"
fi

echo ""
echo -e "${YELLOW}ISSUE 5: Checking Daphne logs for actual errors${NC}"
echo "Last 20 lines from Daphne:"
sudo journalctl -u daphne -n 20 --no-pager

echo ""
echo ""
echo "=========================================="
echo "RECOMMENDED FIX SEQUENCE:"
echo "=========================================="
echo ""
echo "1. Fix Nginx static path (if needed):"
echo "   sudo sed -i 's|/var/www/scan2food/staticfiles/|/var/www/scan2food/static/|g' /etc/nginx/sites-available/scan2food"
echo "   sudo systemctl restart nginx"
echo ""
echo "2. Verify static files have API keys:"
echo "   grep '05XnhaghUWM6Hd7YVR6' /var/www/scan2food/static/theatre_js/live-orders/worker.js"
echo ""
echo "3. Test what Nginx serves:"
echo "   curl -s https://calculatentrade.com/static/theatre_js/live-orders/worker.js | grep 'ws_key'"
echo ""
echo "4. Check browser console for WebSocket URL:"
echo "   Should see: wss://calculatentrade.com/ws/all-seat-datasocket/?key=05XnhaghUWM6Hd7YVR6_iPcJGfH_YDn3RiDv1Rh-zNM"
echo ""
echo "5. Monitor Daphne logs:"
echo "   sudo journalctl -u daphne -f"
echo ""
