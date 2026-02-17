#!/bin/bash

echo "=========================================="
echo "DIAGNOSING 504 GATEWAY TIMEOUT ERROR"
echo "=========================================="
echo ""

# Check if services are running
echo "1. Checking Service Status..."
echo "-------------------------------------------"
echo "Daphne Status:"
sudo systemctl status daphne --no-pager | grep -E "Active:|Main PID:|Memory:|CPU:"
echo ""
echo "Gunicorn Status:"
sudo systemctl status gunicorn --no-pager | grep -E "Active:|Main PID:|Memory:|CPU:"
echo ""
echo "Nginx Status:"
sudo systemctl status nginx --no-pager | grep -E "Active:|Main PID:"
echo ""

# Check for errors in logs
echo "2. Checking Recent Errors..."
echo "-------------------------------------------"
echo "Daphne Errors (last 20 lines):"
sudo journalctl -u daphne -n 20 --no-pager | grep -i "error\|exception\|failed\|timeout"
echo ""
echo "Gunicorn Errors (last 20 lines):"
sudo journalctl -u gunicorn -n 20 --no-pager | grep -i "error\|exception\|failed\|timeout"
echo ""
echo "Nginx Errors (last 20 lines):"
sudo tail -n 20 /var/log/nginx/error.log
echo ""

# Check database connection
echo "3. Checking Database Connection..."
echo "-------------------------------------------"
sudo -u postgres psql -U scan2food_user -d scan2food_db -c "SELECT 1;" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Database connection OK"
else
    echo "✗ Database connection FAILED"
fi
echo ""

# Check Redis connection
echo "4. Checking Redis Connection..."
echo "-------------------------------------------"
redis-cli -a scann2Food PING > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Redis connection OK"
else
    echo "✗ Redis connection FAILED"
fi
echo ""

# Check system resources
echo "5. Checking System Resources..."
echo "-------------------------------------------"
echo "Memory Usage:"
free -h
echo ""
echo "Disk Usage:"
df -h /
echo ""
echo "CPU Load:"
uptime
echo ""

# Check Nginx timeout settings
echo "6. Checking Nginx Timeout Settings..."
echo "-------------------------------------------"
grep -E "proxy_read_timeout|proxy_connect_timeout|proxy_send_timeout" /etc/nginx/sites-available/scan2food
echo ""

# Check for slow queries
echo "7. Checking for Slow Database Queries..."
echo "-------------------------------------------"
echo "Active database connections:"
sudo -u postgres psql -U scan2food_user -d scan2food_db -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"
echo ""

# Check worker processes
echo "8. Checking Worker Processes..."
echo "-------------------------------------------"
echo "Daphne processes:"
ps aux | grep daphne | grep -v grep | wc -l
echo "Gunicorn processes:"
ps aux | grep gunicorn | grep -v grep | wc -l
echo ""

echo "=========================================="
echo "DIAGNOSIS COMPLETE"
echo "=========================================="
echo ""
echo "COMMON CAUSES OF 504 ERRORS:"
echo "1. Database query taking too long"
echo "2. Redis connection timeout"
echo "3. Application code hanging/blocking"
echo "4. Insufficient server resources (RAM/CPU)"
echo "5. Too many concurrent requests"
echo ""
echo "QUICK FIXES:"
echo "1. Restart services: sudo systemctl restart daphne gunicorn nginx"
echo "2. Check logs: sudo journalctl -u daphne -f"
echo "3. Increase Nginx timeout (if needed)"
echo ""
