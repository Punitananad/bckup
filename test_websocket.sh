#!/bin/bash

echo "============================================================"
echo "WEBSOCKET CONNECTION TEST"
echo "============================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test 1: Check if Daphne is running
echo -e "${YELLOW}[1/7] Checking Daphne service...${NC}"
if sudo systemctl is-active --quiet daphne; then
    echo -e "${GREEN}✓ Daphne is running${NC}"
else
    echo -e "${RED}✗ Daphne is NOT running${NC}"
    echo "Starting Daphne..."
    sudo systemctl start daphne
    sleep 2
fi
echo ""

# Test 2: Check port 8001
echo -e "${YELLOW}[2/7] Checking port 8001...${NC}"
PORT_CHECK=$(sudo ss -tlnp | grep 8001)
if [ -n "$PORT_CHECK" ]; then
    echo -e "${GREEN}✓ Port 8001 is listening${NC}"
    echo "$PORT_CHECK"
else
    echo -e "${RED}✗ Port 8001 is NOT listening${NC}"
fi
echo ""

# Test 3: Check CHANNEL_LAYERS configuration
echo -e "${YELLOW}[3/7] Checking CHANNEL_LAYERS configuration...${NC}"
cd /var/www/scan2food/application/scan2food
if grep -q "InMemoryChannelLayer" theatreApp/settings.py; then
    echo -e "${GREEN}✓ Using InMemoryChannelLayer (correct)${NC}"
elif grep -q "RedisChannelLayer" theatreApp/settings.py; then
    echo -e "${RED}✗ Still using RedisChannelLayer (needs fix)${NC}"
else
    echo -e "${RED}✗ CHANNEL_LAYERS not found${NC}"
fi
echo ""

# Test 4: Test HTTP connection to Daphne
echo -e "${YELLOW}[4/7] Testing HTTP connection to Daphne...${NC}"
HTTP_TEST=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/)
if [ "$HTTP_TEST" = "200" ] || [ "$HTTP_TEST" = "301" ] || [ "$HTTP_TEST" = "302" ]; then
    echo -e "${GREEN}✓ Daphne responding (HTTP $HTTP_TEST)${NC}"
else
    echo -e "${RED}✗ Daphne not responding properly (HTTP $HTTP_TEST)${NC}"
fi
echo ""

# Test 5: Test WebSocket route
echo -e "${YELLOW}[5/7] Testing WebSocket route...${NC}"
WS_TEST=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/ws/all-seat-datasocket/)
if [ "$WS_TEST" = "200" ] || [ "$WS_TEST" = "101" ] || [ "$WS_TEST" = "426" ]; then
    echo -e "${GREEN}✓ WebSocket route exists (HTTP $WS_TEST)${NC}"
    echo "  Note: 426 = Upgrade Required (normal for WebSocket)"
elif [ "$WS_TEST" = "404" ]; then
    echo -e "${RED}✗ WebSocket route not found (HTTP 404)${NC}"
else
    echo -e "${YELLOW}⚠ Unexpected response (HTTP $WS_TEST)${NC}"
fi
echo ""

# Test 6: Check recent Daphne logs for errors
echo -e "${YELLOW}[6/7] Checking recent Daphne logs...${NC}"
ERRORS=$(sudo journalctl -u daphne -n 20 --no-pager | grep -i "error\|exception\|failed" | wc -l)
if [ "$ERRORS" -eq 0 ]; then
    echo -e "${GREEN}✓ No errors in recent logs${NC}"
else
    echo -e "${RED}✗ Found $ERRORS error(s) in logs${NC}"
    echo "Recent errors:"
    sudo journalctl -u daphne -n 20 --no-pager | grep -i "error\|exception\|failed"
fi
echo ""

# Test 7: Test WebSocket with websocat (if available)
echo -e "${YELLOW}[7/7] Testing WebSocket connection...${NC}"
if command -v websocat &> /dev/null; then
    echo "Using websocat to test WebSocket..."
    timeout 3 websocat ws://127.0.0.1:8001/ws/all-seat-datasocket/ 2>&1 | head -5
else
    echo "websocat not installed, using curl..."
    curl -i -N \
        -H "Connection: Upgrade" \
        -H "Upgrade: websocket" \
        -H "Sec-WebSocket-Version: 13" \
        -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
        http://127.0.0.1:8001/ws/all-seat-datasocket/ 2>&1 | head -15
fi
echo ""

echo "============================================================"
echo "TEST SUMMARY"
echo "============================================================"
echo ""

# Summary
DAPHNE_STATUS=$(sudo systemctl is-active daphne)
PORT_STATUS=$(sudo ss -tlnp | grep 8001 | wc -l)
CHANNEL_STATUS=$(grep -q "InMemoryChannelLayer" /var/www/scan2food/application/scan2food/theatreApp/settings.py && echo "OK" || echo "FAIL")

if [ "$DAPHNE_STATUS" = "active" ] && [ "$PORT_STATUS" -gt 0 ] && [ "$CHANNEL_STATUS" = "OK" ]; then
    echo -e "${GREEN}✓ WebSocket appears to be configured correctly!${NC}"
    echo ""
    echo "Next step: Test in browser"
    echo "1. Open https://calculatentrade.com"
    echo "2. Open browser console (F12)"
    echo "3. Run: const ws = new WebSocket('wss://calculatentrade.com/ws/all-seat-datasocket/');"
    echo "4. Check for connection success"
else
    echo -e "${RED}✗ WebSocket has issues${NC}"
    echo ""
    echo "Issues found:"
    [ "$DAPHNE_STATUS" != "active" ] && echo "  - Daphne is not running"
    [ "$PORT_STATUS" -eq 0 ] && echo "  - Port 8001 is not listening"
    [ "$CHANNEL_STATUS" != "OK" ] && echo "  - CHANNEL_LAYERS not using InMemoryChannelLayer"
    echo ""
    echo "Run these commands to fix:"
    echo "  sudo systemctl restart daphne"
    echo "  sudo journalctl -u daphne -f"
fi
echo ""

echo "============================================================"
echo "DETAILED LOGS (Last 30 lines)"
echo "============================================================"
sudo journalctl -u daphne -n 30 --no-pager
echo ""
