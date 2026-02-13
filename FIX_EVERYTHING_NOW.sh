#!/bin/bash

# Complete WebSocket Fix Script
# Run on server: bash FIX_EVERYTHING_NOW.sh

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         WebSocket Complete Fix Script                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ============================================================
# STEP 1: Diagnose Current State
# ============================================================
echo -e "${BLUE}[STEP 1] Diagnosing current state...${NC}"
echo ""

echo "Checking Django STATIC_ROOT configuration..."
if grep -q "STATIC_ROOT = '/var/www/scan2food/static'" /var/www/scan2food/application/scan2food/theatreApp/settings.py; then
    echo -e "${GREEN}✓ Django STATIC_ROOT: /var/www/scan2food/static${NC}"
else
    echo -e "${RED}❌ Django STATIC_ROOT not found or incorrect${NC}"
fi

echo ""
echo "Checking Nginx static configuration..."
NGINX_STATIC_PATH=$(grep -A 1 "location /static" /etc/nginx/sites-available/scan2food | grep "alias" | awk '{print $2}' | tr -d ';')
echo "Nginx serves from: $NGINX_STATIC_PATH"

if [[ "$NGINX_STATIC_PATH" == "/var/www/scan2food/static/" ]]; then
    echo -e "${GREEN}✓ Nginx path is correct${NC}"
    NEEDS_NGINX_FIX=false
else
    echo -e "${RED}❌ Nginx path is WRONG (should be /var/www/scan2food/static/)${NC}"
    NEEDS_NGINX_FIX=true
fi

echo ""
echo "Checking if API key exists in static file on disk..."
if grep -q "05XnhaghUWM6Hd7YVR6" /var/www/scan2food/static/theatre_js/live-orders/worker.js 2>/dev/null; then
    echo -e "${GREEN}✓ API key found in file on disk${NC}"
else
    echo -e "${RED}❌ API key NOT in file on disk${NC}"
    echo "   Need to run collectstatic"
fi

echo ""
echo "Checking what Nginx actually serves..."
if curl -s https://calculatentrade.com/static/theatre_js/live-orders/worker.js 2>/dev/null | grep -q "05XnhaghUWM6Hd7YVR6"; then
    echo -e "${GREEN}✓ API key is being served by Nginx${NC}"
else
    echo -e "${RED}❌ API key NOT in served file${NC}"
fi

echo ""
echo "Press Enter to continue with fixes, or Ctrl+C to cancel..."
read

# ============================================================
# STEP 2: Fix Nginx Configuration
# ============================================================
if [ "$NEEDS_NGINX_FIX" = true ]; then
    echo ""
    echo -e "${BLUE}[STEP 2] Fixing Nginx configuration...${NC}"
    echo ""
    
    # Backup
    BACKUP_FILE="/etc/nginx/sites-available/scan2food.backup.$(date +%Y%m%d_%H%M%S)"
    echo "Creating backup: $BACKUP_FILE"
    sudo cp /etc/nginx/sites-available/scan2food "$BACKUP_FILE"
    echo -e "${GREEN}✓ Backup created${NC}"
    
    # Fix the path
    echo "Fixing static path..."
    sudo sed -i 's|/var/www/scan2food/staticfiles/|/var/www/scan2food/static/|g' /etc/nginx/sites-available/scan2food
    
    # Verify the change
    NEW_PATH=$(grep -A 1 "location /static" /etc/nginx/sites-available/scan2food | grep "alias" | awk '{print $2}' | tr -d ';')
    if [[ "$NEW_PATH" == "/var/www/scan2food/static/" ]]; then
        echo -e "${GREEN}✓ Path updated successfully${NC}"
    else
        echo -e "${RED}❌ Path update failed${NC}"
        echo "Restoring backup..."
        sudo cp "$BACKUP_FILE" /etc/nginx/sites-available/scan2food
        exit 1
    fi
    
    # Test nginx config
    echo "Testing Nginx configuration..."
    if sudo nginx -t 2>&1 | grep -q "successful"; then
        echo -e "${GREEN}✓ Nginx config is valid${NC}"
    else
        echo -e "${RED}❌ Nginx config has errors${NC}"
        sudo nginx -t
        echo "Restoring backup..."
        sudo cp "$BACKUP_FILE" /etc/nginx/sites-available/scan2food
        exit 1
    fi
    
    # Restart nginx
    echo "Restarting Nginx..."
    sudo systemctl restart nginx
    echo -e "${GREEN}✓ Nginx restarted${NC}"
else
    echo ""
    echo -e "${BLUE}[STEP 2] Nginx configuration is already correct${NC}"
fi

# ============================================================
# STEP 3: Add Cache Control Headers
# ============================================================
echo ""
echo -e "${BLUE}[STEP 3] Adding cache control headers for JS files...${NC}"
echo ""

if grep -q "location ~\* \\\.js\$" /etc/nginx/sites-available/scan2food; then
    echo -e "${GREEN}✓ Cache control headers already exist${NC}"
else
    echo "Adding cache control headers..."
    
    # Create a temporary file with the new configuration
    sudo awk '
    /location \/static\/ \{/ {
        print
        print "        # Prevent caching of JavaScript files"
        print "        location ~* \\.js$ {"
        print "            add_header Cache-Control \"no-cache, no-store, must-revalidate\";"
        print "            add_header Pragma \"no-cache\";"
        print "            add_header Expires \"0\";"
        print "        }"
        next
    }
    {print}
    ' /etc/nginx/sites-available/scan2food > /tmp/scan2food.tmp
    
    sudo mv /tmp/scan2food.tmp /etc/nginx/sites-available/scan2food
    
    # Test and restart
    if sudo nginx -t 2>&1 | grep -q "successful"; then
        sudo systemctl restart nginx
        echo -e "${GREEN}✓ Cache headers added and Nginx restarted${NC}"
    else
        echo -e "${RED}❌ Failed to add cache headers${NC}"
        sudo cp "$BACKUP_FILE" /etc/nginx/sites-available/scan2food
        sudo systemctl restart nginx
    fi
fi

# ============================================================
# STEP 4: Verify Static Files
# ============================================================
echo ""
echo -e "${BLUE}[STEP 4] Verifying static files...${NC}"
echo ""

echo "Checking if API key is in static file on disk..."
if grep -q "05XnhaghUWM6Hd7YVR6" /var/www/scan2food/static/theatre_js/live-orders/worker.js; then
    echo -e "${GREEN}✓ API key found${NC}"
else
    echo -e "${YELLOW}⚠ API key not found - running collectstatic...${NC}"
    cd /var/www/scan2food/application/scan2food
    source venv/bin/activate
    python manage.py collectstatic --noinput --clear
    
    if grep -q "05XnhaghUWM6Hd7YVR6" /var/www/scan2food/static/theatre_js/live-orders/worker.js; then
        echo -e "${GREEN}✓ API key now present after collectstatic${NC}"
    else
        echo -e "${RED}❌ API key still missing - check source files${NC}"
    fi
fi

# ============================================================
# STEP 5: Test What Nginx Serves
# ============================================================
echo ""
echo -e "${BLUE}[STEP 5] Testing what Nginx actually serves...${NC}"
echo ""

sleep 2  # Give Nginx a moment

echo "Fetching worker.js from live server..."
if curl -s https://calculatentrade.com/static/theatre_js/live-orders/worker.js | grep -q "05XnhaghUWM6Hd7YVR6"; then
    echo -e "${GREEN}✓ API key is being served correctly!${NC}"
else
    echo -e "${RED}❌ API key still not in served file${NC}"
    echo ""
    echo "First 30 lines of served file:"
    curl -s https://calculatentrade.com/static/theatre_js/live-orders/worker.js | head -30
fi

# ============================================================
# STEP 6: Check Services
# ============================================================
echo ""
echo -e "${BLUE}[STEP 6] Checking services status...${NC}"
echo ""

services=("gunicorn" "daphne" "nginx" "redis-server")
for service in "${services[@]}"; do
    if systemctl is-active --quiet "$service"; then
        echo -e "${GREEN}✓ $service is running${NC}"
    else
        echo -e "${RED}❌ $service is NOT running${NC}"
    fi
done

# ============================================================
# STEP 7: Show Recent Daphne Logs
# ============================================================
echo ""
echo -e "${BLUE}[STEP 7] Recent Daphne logs (last 10 lines):${NC}"
echo ""
sudo journalctl -u daphne -n 10 --no-pager

# ============================================================
# FINAL SUMMARY
# ============================================================
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    FIX COMPLETE                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${YELLOW}NEXT STEPS:${NC}"
echo ""
echo "1. Users must do HARD REFRESH in browser:"
echo "   • Chrome/Firefox: Ctrl + Shift + R"
echo "   • Safari: Cmd + Shift + R"
echo ""
echo "2. Check browser console (F12):"
echo "   • Network tab → Look for WebSocket connection"
echo "   • URL should include: ?key=05XnhaghUWM6Hd7YVR6_iPcJGfH_YDn3RiDv1Rh-zNM"
echo ""
echo "3. Monitor Daphne logs in real-time:"
echo "   sudo journalctl -u daphne -f"
echo ""
echo "   Should see: WSCONNECT (not WSREJECT)"
echo ""
echo -e "${YELLOW}SECURITY NOTE:${NC}"
echo "The current API key system works but is not ideal."
echo "Consider migrating to session-based authentication."
echo "See: BETTER_WEBSOCKET_AUTH.md"
echo ""
