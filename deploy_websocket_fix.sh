#!/bin/bash

echo "============================================================"
echo "DEPLOYING WEBSOCKET FIX"
echo "============================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Navigate to project directory
cd /var/www/scan2food

# Step 1: Pull latest changes
echo -e "${YELLOW}[1/6] Pulling latest changes from GitHub...${NC}"
git stash
git pull origin main
git stash pop
echo -e "${GREEN}✓ Code updated${NC}"
echo ""

# Step 2: Activate virtual environment
echo -e "${YELLOW}[2/6] Activating virtual environment...${NC}"
cd application/scan2food
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Step 3: Verify channels installation
echo -e "${YELLOW}[3/6] Verifying Django Channels installation...${NC}"
python -c "import channels; print('Channels version:', channels.__version__)" 2>&1
if [ $? -ne 0 ]; then
    echo -e "${RED}Installing channels...${NC}"
    pip install channels daphne
fi
echo -e "${GREEN}✓ Channels verified${NC}"
echo ""

# Step 4: Verify ASGI configuration
echo -e "${YELLOW}[4/6] Verifying ASGI configuration...${NC}"
if grep -q "InMemoryChannelLayer" theatreApp/settings.py; then
    echo -e "${GREEN}✓ CHANNEL_LAYERS updated to InMemoryChannelLayer${NC}"
else
    echo -e "${RED}⚠ CHANNEL_LAYERS still using Redis${NC}"
    echo "Please update settings.py manually"
fi
echo ""

# Step 5: Restart services
echo -e "${YELLOW}[5/6] Restarting services...${NC}"
sudo systemctl restart daphne
sleep 2
sudo systemctl restart gunicorn
sudo systemctl restart nginx
echo -e "${GREEN}✓ Services restarted${NC}"
echo ""

# Step 6: Verify services are running
echo -e "${YELLOW}[6/6] Verifying services...${NC}"
echo ""
echo "Daphne status:"
sudo systemctl is-active daphne && echo -e "${GREEN}✓ Daphne is running${NC}" || echo -e "${RED}✗ Daphne failed${NC}"
echo ""
echo "Gunicorn status:"
sudo systemctl is-active gunicorn && echo -e "${GREEN}✓ Gunicorn is running${NC}" || echo -e "${RED}✗ Gunicorn failed${NC}"
echo ""
echo "Nginx status:"
sudo systemctl is-active nginx && echo -e "${GREEN}✓ Nginx is running${NC}" || echo -e "${RED}✗ Nginx failed${NC}"
echo ""

# Check port 8001
echo "Port 8001 (Daphne):"
sudo ss -tlnp | grep 8001
echo ""

# Test WebSocket endpoint
echo -e "${YELLOW}Testing WebSocket endpoint...${NC}"
curl -I http://127.0.0.1:8001/ws/all-seat-datasocket/ 2>&1 | head -10
echo ""

echo "============================================================"
echo "DEPLOYMENT COMPLETE"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Test WebSocket in browser: wss://calculatentrade.com/ws/all-seat-datasocket/"
echo "2. Check browser console for WebSocket connection"
echo "3. If issues persist, check logs:"
echo "   - Daphne: sudo journalctl -u daphne -f"
echo "   - Nginx: sudo tail -f /var/log/nginx/error.log"
echo ""
