#!/bin/bash
# Enable Redis for WebSocket Communication

echo "=========================================="
echo "ENABLING REDIS FOR WEBSOCKET"
echo "=========================================="
echo ""

# 1. Check Redis is working
echo "1. Testing Redis Connection:"
redis-cli ping
echo ""

# 2. Restart services
echo "2. Restarting Gunicorn and Daphne..."
sudo systemctl restart gunicorn
sleep 2
sudo systemctl restart daphne
sleep 2
echo "Services restarted!"
echo ""

# 3. Check service status
echo "3. Checking Service Status:"
echo ""
echo "Gunicorn:"
sudo systemctl status gunicorn --no-pager | grep -E "Active|Memory"
echo ""
echo "Daphne:"
sudo systemctl status daphne --no-pager | grep -E "Active|Memory"
echo ""
echo "Redis:"
sudo systemctl status redis-server --no-pager | grep -E "Active|Memory"
echo ""

# 4. Check memory usage
echo "4. Memory Usage:"
free -h
echo ""

# 5. Test channel layer
echo "5. Testing Channel Layer Configuration:"
cd /var/www/scan2food/application/scan2food
source venv/bin/activate
python3 << 'EOF'
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theatreApp.settings')
django.setup()

from channels.layers import get_channel_layer
channel_layer = get_channel_layer()
print(f"✅ Channel Layer Backend: {channel_layer.__class__.__name__}")
print(f"✅ Using Redis: {'Redis' in channel_layer.__class__.__name__}")
EOF
echo ""

echo "=========================================="
echo "SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "Next Steps:"
echo "1. Open live orders page: https://calculatentrade.com/theatre/live-orders"
echo "2. Create a new order from another device/browser"
echo "3. Order should appear INSTANTLY without refresh!"
echo ""
echo "If it doesn't work, check logs:"
echo "  sudo journalctl -u daphne -f"
echo "  sudo journalctl -u gunicorn -f"
