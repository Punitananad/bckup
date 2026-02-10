#!/bin/bash

echo "============================================================"
echo "WEBSOCKET CONFIGURATION CHECK"
echo "============================================================"
echo ""

# Check 1: Verify ASGI file content
echo "[1] ASGI Configuration:"
echo "---"
cat /var/www/scan2food/application/scan2food/theatreApp/asgi.py
echo ""
echo ""

# Check 2: Verify Daphne service file
echo "[2] Daphne Service Configuration:"
echo "---"
if [ -f "/etc/systemd/system/daphne.service" ]; then
    cat /etc/systemd/system/daphne.service
else
    echo "ERROR: Daphne service file not found!"
fi
echo ""
echo ""

# Check 3: Check if Daphne is running
echo "[3] Daphne Service Status:"
echo "---"
sudo systemctl status daphne --no-pager | head -20
echo ""
echo ""

# Check 4: Check what's listening on port 8001
echo "[4] Port 8001 Status:"
echo "---"
sudo ss -tlnp | grep 8001
echo ""
echo ""

# Check 5: Test Daphne directly
echo "[5] Direct Daphne Test (HTTP):"
echo "---"
curl -v http://127.0.0.1:8001/ 2>&1 | head -20
echo ""
echo ""

# Check 6: Test WebSocket route
echo "[6] WebSocket Route Test:"
echo "---"
curl -v http://127.0.0.1:8001/ws/all-seat-datasocket/ 2>&1 | head -20
echo ""
echo ""

# Check 7: Check Django settings for ASGI_APPLICATION
echo "[7] Django ASGI_APPLICATION Setting:"
echo "---"
cd /var/www/scan2food/application/scan2food
source venv/bin/activate
python -c "from django.conf import settings; import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theatreApp.settings'); import django; django.setup(); print('ASGI_APPLICATION:', getattr(settings, 'ASGI_APPLICATION', 'NOT SET'))"
echo ""
echo ""

# Check 8: Verify channels is installed
echo "[8] Django Channels Installation:"
echo "---"
python -c "import channels; print('Channels version:', channels.__version__)"
echo ""
echo ""

# Check 9: Recent Daphne logs
echo "[9] Recent Daphne Logs:"
echo "---"
sudo journalctl -u daphne -n 30 --no-pager
echo ""
echo ""

echo "============================================================"
echo "CHECK COMPLETE"
echo "============================================================"
