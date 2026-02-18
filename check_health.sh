#!/bin/bash

# Quick Health Check Script for Scan2Food
# Usage: bash check_health.sh

echo "=========================================="
echo "SCAN2FOOD HEALTH CHECK"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check services
echo "Service Status:"
echo "---------------"

services=("gunicorn" "daphne" "nginx" "redis")
all_running=true

for service in "${services[@]}"; do
    if systemctl is-active --quiet $service; then
        echo -e "${GREEN}✓ $service is running${NC}"
    else
        echo -e "${RED}✗ $service is NOT running${NC}"
        all_running=false
    fi
done

echo ""

# Check WebSocket
echo "WebSocket Status:"
echo "-----------------"

if systemctl is-active --quiet redis; then
    echo -e "${GREEN}✓ Redis is running (WebSocket backend)${NC}"
else
    echo -e "${RED}✗ Redis is NOT running - WebSocket will not work!${NC}"
fi

if netstat -tuln | grep -q ":8001"; then
    echo -e "${GREEN}✓ Daphne is listening on port 8001 (WebSocket)${NC}"
else
    echo -e "${RED}✗ Daphne is NOT listening on WebSocket port${NC}"
fi

echo ""

# Check website
echo "Website Status:"
echo "---------------"

http_code=$(curl -s -o /dev/null -w "%{http_code}" https://www.calculatentrade.com)
if [ "$http_code" = "200" ] || [ "$http_code" = "301" ] || [ "$http_code" = "302" ]; then
    echo -e "${GREEN}✓ Website is responding (HTTP $http_code)${NC}"
else
    echo -e "${RED}✗ Website returned HTTP $http_code${NC}"
fi

echo ""

# Summary
echo "=========================================="
if [ "$all_running" = true ]; then
    echo -e "${GREEN}All services are healthy!${NC}"
else
    echo -e "${RED}Some services need attention!${NC}"
    echo ""
    echo "To restart services:"
    echo "  sudo systemctl restart gunicorn"
    echo "  sudo systemctl restart daphne"
    echo "  sudo systemctl restart nginx"
    echo "  sudo systemctl restart redis"
fi
echo "=========================================="
