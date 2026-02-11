#!/bin/bash

# Automated Deployment Script for Scan2Food
# Usage: bash deploy.sh

set -e  # Exit on any error

echo "=========================================="
echo "SCAN2FOOD AUTOMATED DEPLOYMENT"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Project paths
PROJECT_DIR="/var/www/scan2food"
APP_DIR="$PROJECT_DIR/application/scan2food"
VENV_DIR="$APP_DIR/venv"

echo -e "${YELLOW}Step 1: Pulling latest code from GitHub...${NC}"
cd $PROJECT_DIR
git pull origin main
echo -e "${GREEN}✓ Code updated${NC}"
echo ""

echo -e "${YELLOW}Step 2: Checking .env file for WebSocket keys...${NC}"
if ! grep -q "LIVE_ORDERS_WS_KEY" "$APP_DIR/.env" 2>/dev/null; then
    echo -e "${YELLOW}Adding WebSocket security keys to .env file...${NC}"
    cat >> "$APP_DIR/.env" << 'EOF'

# WebSocket Security Keys
LIVE_ORDERS_WS_KEY=05XnhaghUWM6Hd7YVR6_iPcJGfH_YDn3RiDv1Rh-zNM
PAYMENT_STATUS_WS_KEY=vy8ALNb9ev6DvTFGHv9IC3RgQ0xL5shqNmnFmDEHNqM
CHAT_WS_KEY=A0B9sna1Pdio-1MdXHG8kQJwuC_45Ok2ZmlQbS_0B-U
EOF
    echo -e "${GREEN}✓ WebSocket keys added${NC}"
else
    echo -e "${GREEN}✓ WebSocket keys already present${NC}"
fi
echo ""

echo -e "${YELLOW}Step 3: Activating virtual environment...${NC}"
source $VENV_DIR/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

echo -e "${YELLOW}Step 4: Installing/updating dependencies...${NC}"
cd $APP_DIR
pip install -r requirements.txt --quiet
echo -e "${GREEN}✓ Dependencies updated${NC}"
echo ""

echo -e "${YELLOW}Step 5: Running database migrations...${NC}"
python manage.py migrate --noinput
echo -e "${GREEN}✓ Migrations completed${NC}"
echo ""

echo -e "${YELLOW}Step 6: Collecting static files...${NC}"
python manage.py collectstatic --noinput
echo -e "${GREEN}✓ Static files collected${NC}"
echo ""

echo -e "${YELLOW}Step 7: Restarting services...${NC}"
sudo systemctl restart gunicorn
echo -e "${GREEN}✓ Gunicorn restarted${NC}"

sudo systemctl restart daphne
echo -e "${GREEN}✓ Daphne restarted${NC}"

sudo systemctl restart nginx
echo -e "${GREEN}✓ Nginx restarted${NC}"
echo ""

echo -e "${YELLOW}Step 8: Checking service status...${NC}"
echo ""
echo "Gunicorn Status:"
sudo systemctl status gunicorn --no-pager -l | head -n 5
echo ""
echo "Daphne Status:"
sudo systemctl status daphne --no-pager -l | head -n 5
echo ""
echo "Nginx Status:"
sudo systemctl status nginx --no-pager -l | head -n 3
echo ""

echo "=========================================="
echo -e "${GREEN}DEPLOYMENT COMPLETE!${NC}"
echo "=========================================="
echo ""
echo "Your application is now running with:"
echo "  ✓ Latest code from GitHub"
echo "  ✓ WebSocket security enabled"
echo "  ✓ Updated static files"
echo "  ✓ All services restarted"
echo ""
echo "Website: https://www.calculatentrade.com"
echo ""
echo "To view logs:"
echo "  Gunicorn: sudo journalctl -u gunicorn -f"
echo "  Daphne:   sudo journalctl -u daphne -f"
echo "  Nginx:    sudo tail -f /var/log/nginx/error.log"
echo ""
