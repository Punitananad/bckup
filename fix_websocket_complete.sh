#!/bin/bash

echo "============================================================"
echo "WEBSOCKET CONFIGURATION DIAGNOSTIC & FIX"
echo "============================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Check if Daphne is running
echo -e "${YELLOW}[1/8] Checking Daphne service...${NC}"
if sudo systemctl is-active --quiet daphne; then
    echo -e "${GREEN}✓ Daphne is running${NC}"
    sudo ss -tlnp | grep 8001
else
    echo -e "${RED}✗ Daphne is NOT running${NC}"
    echo "Starting Daphne..."
    sudo systemctl start daphne
    sleep 2
    sudo systemctl status daphne --no-pager
fi
echo ""

# 2. Check Nginx configuration
echo -e "${YELLOW}[2/8] Checking Nginx WebSocket configuration...${NC}"
if grep -q "proxy_pass http://127.0.0.1:8001" /etc/nginx/sites-available/scan2food; then
    echo -e "${GREEN}✓ Nginx has Daphne proxy configuration${NC}"
else
    echo -e "${RED}✗ Nginx missing Daphne proxy${NC}"
fi

if grep -q "Upgrade \$http_upgrade" /etc/nginx/sites-available/scan2food; then
    echo -e "${GREEN}✓ Nginx has WebSocket upgrade headers${NC}"
else
    echo -e "${RED}✗ Nginx missing WebSocket headers${NC}"
fi
echo ""

# 3. Test Daphne directly
echo -e "${YELLOW}[3/8] Testing Daphne directly (port 8001)...${NC}"
curl -I http://127.0.0.1:8001/ 2>&1 | head -5
echo ""

# 4. Test WebSocket route through Daphne
echo -e "${YELLOW}[4/8] Testing WebSocket route on Daphne...${NC}"
curl -I http://127.0.0.1:8001/ws/all-seat-datasocket/ 2>&1 | head -5
echo ""

# 5. Check ASGI file
echo -e "${YELLOW}[5/8] Checking ASGI configuration...${NC}"
if grep -q "ProtocolTypeRouter" /var/www/scan2food/application/scan2food/theatreApp/asgi.py; then
    echo -e "${GREEN}✓ ASGI has ProtocolTypeRouter${NC}"
else
    echo -e "${RED}✗ ASGI missing ProtocolTypeRouter${NC}"
fi

if grep -q "websocket" /var/www/scan2food/application/scan2food/theatreApp/asgi.py; then
    echo -e "${GREEN}✓ ASGI has websocket protocol${NC}"
else
    echo -e "${RED}✗ ASGI missing websocket protocol${NC}"
fi
echo ""

# 6. Check routing files
echo -e "${YELLOW}[6/8] Checking routing files...${NC}"
if [ -f "/var/www/scan2food/application/scan2food/theatre/routing.py" ]; then
    echo -e "${GREEN}✓ theatre/routing.py exists${NC}"
    grep "path" /var/www/scan2food/application/scan2food/theatre/routing.py
else
    echo -e "${RED}✗ theatre/routing.py missing${NC}"
fi

if [ -f "/var/www/scan2food/application/scan2food/chat_box/routing.py" ]; then
    echo -e "${GREEN}✓ chat_box/routing.py exists${NC}"
    grep "path" /var/www/scan2food/application/scan2food/chat_box/routing.py
else
    echo -e "${RED}✗ chat_box/routing.py missing${NC}"
fi
echo ""

# 7. Check if channels is installed
echo -e "${YELLOW}[7/8] Checking Django Channels installation...${NC}"
cd /var/www/scan2food/application/scan2food
source venv/bin/activate
python -c "import channels; print('Channels version:', channels.__version__)" 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Django Channels is installed${NC}"
else
    echo -e "${RED}✗ Django Channels is NOT installed${NC}"
    echo "Installing channels..."
    pip install channels channels-redis daphne
fi
echo ""

# 8. Check Daphne logs
echo -e "${YELLOW}[8/8] Recent Daphne logs:${NC}"
sudo journalctl -u daphne -n 20 --no-pager
echo ""

echo "============================================================"
echo "DIAGNOSTIC COMPLETE"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. If Daphne is not running: sudo systemctl start daphne"
echo "2. If channels not installed: pip install channels channels-redis daphne"
echo "3. Restart all services: sudo systemctl restart daphne gunicorn nginx"
echo "4. Test WebSocket: Open browser console and check WebSocket connection"
echo ""
