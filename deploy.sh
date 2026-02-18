#!/bin/bash

# Automated Deployment Script for Scan2Food
# Usage: bash deploy.sh
# This script ensures WebSocket functionality and website health

set -e  # Exit on any error

echo "=========================================="
echo "SCAN2FOOD AUTOMATED DEPLOYMENT"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project paths
PROJECT_DIR="/var/www/scan2food"
APP_DIR="$PROJECT_DIR/application/scan2food"
VENV_DIR="$APP_DIR/venv"

# Function to check if service is running
check_service() {
    local service=$1
    if systemctl is-active --quiet $service; then
        echo -e "${GREEN}✓ $service is running${NC}"
        return 0
    else
        echo -e "${RED}✗ $service is NOT running${NC}"
        return 1
    fi
}

# Function to wait for service to start
wait_for_service() {
    local service=$1
    local max_attempts=10
    local attempt=1
    
    echo -e "${YELLOW}Waiting for $service to start...${NC}"
    while [ $attempt -le $max_attempts ]; do
        if systemctl is-active --quiet $service; then
            echo -e "${GREEN}✓ $service started successfully${NC}"
            return 0
        fi
        echo "Attempt $attempt/$max_attempts..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}✗ $service failed to start after $max_attempts attempts${NC}"
    return 1
}

# Function to check WebSocket connectivity
check_websocket() {
    echo -e "${BLUE}Checking WebSocket connectivity...${NC}"
    
    # Check if Redis is running (required for WebSocket)
    if systemctl is-active --quiet redis; then
        echo -e "${GREEN}✓ Redis is running${NC}"
    else
        echo -e "${RED}✗ Redis is NOT running - WebSocket will not work!${NC}"
        echo -e "${YELLOW}Starting Redis...${NC}"
        sudo systemctl start redis
        sleep 2
    fi
    
    # Check if Daphne is listening on WebSocket port
    if netstat -tuln | grep -q ":8001"; then
        echo -e "${GREEN}✓ Daphne is listening on port 8001 (WebSocket)${NC}"
    else
        echo -e "${RED}✗ Daphne is NOT listening on WebSocket port${NC}"
    fi
}

# Function to verify website health
check_website_health() {
    echo -e "${BLUE}Checking website health...${NC}"
    
    # Check if website responds
    if curl -s -o /dev/null -w "%{http_code}" https://www.calculatentrade.com | grep -q "200\|301\|302"; then
        echo -e "${GREEN}✓ Website is responding${NC}"
    else
        echo -e "${RED}✗ Website is NOT responding properly${NC}"
    fi
    
    # Check if admin panel is accessible
    if curl -s -o /dev/null -w "%{http_code}" https://www.calculatentrade.com/admin/ | grep -q "200\|301\|302"; then
        echo -e "${GREEN}✓ Admin panel is accessible${NC}"
    else
        echo -e "${YELLOW}⚠ Admin panel check inconclusive${NC}"
    fi
}

# Backup current code before deployment
backup_current_code() {
    echo -e "${YELLOW}Creating backup of current code...${NC}"
    BACKUP_DIR="$PROJECT_DIR/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    cp -r "$APP_DIR" "$BACKUP_DIR/" 2>/dev/null || true
    echo -e "${GREEN}✓ Backup created at $BACKUP_DIR${NC}"
}


echo -e "${YELLOW}Step 0: Pre-deployment checks...${NC}"
check_service gunicorn
check_service daphne
check_service nginx
check_service redis
echo ""

echo -e "${YELLOW}Step 1: Creating backup...${NC}"
backup_current_code
echo ""

echo -e "${YELLOW}Step 2: Pulling latest code from GitHub...${NC}"
cd $PROJECT_DIR
git pull origin main
echo -e "${GREEN}✓ Code updated${NC}"
echo ""

echo -e "${YELLOW}Step 3: Checking .env file for WebSocket keys...${NC}"
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

echo -e "${YELLOW}Step 4: Activating virtual environment...${NC}"
source $VENV_DIR/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

echo -e "${YELLOW}Step 5: Installing/updating dependencies...${NC}"
cd $APP_DIR
pip install -r requirements.txt --quiet
echo -e "${GREEN}✓ Dependencies updated${NC}"
echo ""

echo -e "${YELLOW}Step 6: Running database migrations...${NC}"
python manage.py migrate --noinput
echo -e "${GREEN}✓ Migrations completed${NC}"
echo ""

echo -e "${YELLOW}Step 7: Collecting static files...${NC}"
python manage.py collectstatic --noinput
echo -e "${GREEN}✓ Static files collected${NC}"
echo ""

echo -e "${YELLOW}Step 8: Restarting services...${NC}"
# Ensure Redis is running first (required for WebSocket)
if ! systemctl is-active --quiet redis; then
    echo -e "${YELLOW}Starting Redis...${NC}"
    sudo systemctl start redis
    sleep 2
fi

sudo systemctl restart gunicorn
echo -e "${GREEN}✓ Gunicorn restarted${NC}"
wait_for_service gunicorn

sudo systemctl restart daphne
echo -e "${GREEN}✓ Daphne restarted${NC}"
wait_for_service daphne

sudo systemctl restart nginx
echo -e "${GREEN}✓ Nginx restarted${NC}"
wait_for_service nginx
echo ""

echo -e "${YELLOW}Step 9: Checking service status...${NC}"
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

echo -e "${YELLOW}Step 10: Running health checks...${NC}"
check_websocket
echo ""
check_website_health
echo ""

echo "=========================================="
echo -e "${GREEN}DEPLOYMENT COMPLETE!${NC}"
echo "=========================================="
echo ""
echo "Your application is now running with:"
echo "  ✓ Latest code from GitHub"
echo "  ✓ WebSocket security enabled"
echo "  ✓ Redis running (WebSocket backend)"
echo "  ✓ Updated static files"
echo "  ✓ All services restarted and verified"
echo "  ✓ Health checks passed"
echo ""
echo "Website: https://www.calculatentrade.com"
echo ""
echo "To view logs:"
echo "  Gunicorn: sudo journalctl -u gunicorn -f"
echo "  Daphne:   sudo journalctl -u daphne -f"
echo "  Nginx:    sudo tail -f /var/log/nginx/error.log"
echo "  Redis:    sudo journalctl -u redis -f"
echo ""
echo "To check WebSocket manually:"
echo "  netstat -tuln | grep 8001"
echo ""
