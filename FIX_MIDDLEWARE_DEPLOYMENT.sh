#!/bin/bash
# Fix Middleware Deployment Issues
# This script fixes the gunicorn service file and adds debug logging to middleware

echo "=== FIXING MIDDLEWARE DEPLOYMENT ISSUES ==="
echo ""

# Step 1: Fix gunicorn service file (remove "kk" characters)
echo "Step 1: Fixing gunicorn.service file..."
sudo tee /etc/systemd/system/gunicorn.service > /dev/null << 'EOF'
[Unit]
Description=Gunicorn daemon
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/scan2food/application/scan2food
EnvironmentFile=/var/www/scan2food/application/scan2food/.env
ExecStart=/var/www/scan2food/application/scan2food/venv/bin/gunicorn --workers 2 --bind unix:/var/www/scan2food/application/scan2food/gunicorn.sock theatreApp.wsgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Fixed gunicorn.service (removed 'kk' characters)"
echo ""

# Step 2: Reload systemd to pick up the fixed service file
echo "Step 2: Reloading systemd daemon..."
sudo systemctl daemon-reload
echo "✓ Systemd reloaded"
echo ""

# Step 3: Clear Python bytecode cache
echo "Step 3: Clearing Python bytecode cache..."
cd /var/www/scan2food/application/scan2food
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo "✓ Python cache cleared"
echo ""

# Step 4: Restart services
echo "Step 4: Restarting services..."
sudo systemctl restart gunicorn
sudo systemctl restart daphne
echo "✓ Services restarted"
echo ""

# Step 5: Check service status
echo "Step 5: Checking service status..."
echo ""
echo "--- Gunicorn Status ---"
sudo systemctl status gunicorn --no-pager -l | head -20
echo ""
echo "--- Daphne Status ---"
sudo systemctl status daphne --no-pager -l | head -20
echo ""

# Step 6: Verify API key is loaded
echo "Step 6: Verifying API_KEY environment variable..."
if grep -q "API_KEY=" /var/www/scan2food/application/scan2food/.env; then
    echo "✓ API_KEY found in .env file"
    grep "API_KEY=" /var/www/scan2food/application/scan2food/.env | sed 's/=.*/=***HIDDEN***/'
else
    echo "✗ WARNING: API_KEY not found in .env file!"
fi
echo ""

echo "=== DEPLOYMENT FIX COMPLETE ==="
echo ""
echo "Next steps:"
echo "1. Test the API endpoint WITHOUT API key (should get 401 error)"
echo "2. Test the API endpoint WITH API key (should work)"
echo "3. Check logs: sudo journalctl -u gunicorn -n 50"
