#!/bin/bash
# Fix Out of Memory Issue - Reduce Gunicorn Workers from 4 to 2

echo "=========================================="
echo "FIXING OUT OF MEMORY ISSUE"
echo "=========================================="
echo ""

# Step 1: Show current memory usage
echo "1. Current Memory Usage:"
free -h
echo ""

# Step 2: Show current Gunicorn configuration
echo "2. Current Gunicorn Configuration:"
grep "workers" /etc/systemd/system/gunicorn.service
echo ""

# Step 3: Backup the current configuration
echo "3. Creating backup..."
sudo cp /etc/systemd/system/gunicorn.service /etc/systemd/system/gunicorn.service.backup
echo "Backup created at: /etc/systemd/system/gunicorn.service.backup"
echo ""

# Step 4: Update workers from 4 to 2
echo "4. Updating Gunicorn workers from 4 to 2..."
sudo sed -i 's/--workers 4/--workers 2/g' /etc/systemd/system/gunicorn.service
echo "Configuration updated!"
echo ""

# Step 5: Show new configuration
echo "5. New Gunicorn Configuration:"
grep "workers" /etc/systemd/system/gunicorn.service
echo ""

# Step 6: Reload systemd daemon
echo "6. Reloading systemd daemon..."
sudo systemctl daemon-reload
echo "Done!"
echo ""

# Step 7: Restart Gunicorn
echo "7. Restarting Gunicorn..."
sudo systemctl restart gunicorn
sleep 3
echo "Done!"
echo ""

# Step 8: Check Gunicorn status
echo "8. Checking Gunicorn Status:"
sudo systemctl status gunicorn --no-pager | head -20
echo ""

# Step 9: Show new memory usage
echo "9. New Memory Usage (after fix):"
free -h
echo ""

# Step 10: Show process memory usage
echo "10. Process Memory Usage:"
ps aux --sort=-%mem | head -10
echo ""

echo "=========================================="
echo "FIX COMPLETE!"
echo "=========================================="
echo ""
echo "Your website should now be much faster!"
echo ""
echo "Monitor memory usage with: watch -n 2 free -h"
echo "If still slow, check: sudo systemctl status gunicorn daphne"
