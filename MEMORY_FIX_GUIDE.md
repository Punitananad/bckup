# Memory Issue Fix Guide

## Problem
Your website became very slow after WebSocket setup due to **OUT OF MEMORY** issue.

## Root Cause
- Server has only **961MB RAM** total
- Running too many Gunicorn workers (4 workers × 100MB = 400MB)
- Plus Daphne (125MB) + Redis (50MB) + System (300MB) = **875MB+ total**
- System was swapping memory to disk (causing extreme slowness)

## What Are Workers?
Workers are parallel copies of your Django application that handle requests simultaneously:
- **4 workers** = Can handle 4 requests at the same time (but uses 400MB RAM)
- **2 workers** = Can handle 2 requests at the same time (uses only 200MB RAM)

For your traffic level, 2 workers is sufficient and will free up 200MB of RAM.

## Solution: Reduce Workers from 4 to 2

### Quick Fix (Run on Server)
```bash
# Upload and run the fix script
chmod +x fix_memory_issue.sh
./fix_memory_issue.sh
```

### Manual Fix (If Script Doesn't Work)
```bash
# 1. Backup current config
sudo cp /etc/systemd/system/gunicorn.service /etc/systemd/system/gunicorn.service.backup

# 2. Edit the config
sudo nano /etc/systemd/system/gunicorn.service

# 3. Find this line:
#    --workers 4 \
# Change to:
#    --workers 2 \

# 4. Save and exit (Ctrl+X, Y, Enter)

# 5. Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart gunicorn

# 6. Verify it's working
sudo systemctl status gunicorn
free -h
```

## Verify the Fix

### Check Memory Usage
```bash
# Should show more free memory now
free -h

# Monitor in real-time (Ctrl+C to exit)
watch -n 2 free -h
```

### Check Process Memory
```bash
# See which processes use most memory
ps aux --sort=-%mem | head -10
```

### Check Services Status
```bash
sudo systemctl status gunicorn
sudo systemctl status daphne
sudo systemctl status nginx
```

## Expected Results After Fix
- **Free Memory**: Should increase from 66MB to ~250-300MB
- **CPU Usage**: Should drop from 100% to normal levels
- **Website Speed**: Should return to normal (fast response times)
- **No More**: "WORKER TIMEOUT" errors in logs

## Monitor for 24 Hours
```bash
# Check memory every few hours
free -h

# Check for errors
sudo journalctl -u gunicorn -n 50 --no-pager
sudo journalctl -u daphne -n 50 --no-pager
```

## Long-Term Recommendations

### Option 1: Upgrade Server RAM (Recommended)
- Upgrade from 1GB to 2GB RAM
- Cost: Usually $6-12/month
- Benefit: Can run 4 workers + Daphne comfortably

### Option 2: Disable Daphne When Not Needed
If you don't need real-time WebSocket features:
```bash
# Stop Daphne to free 125MB RAM
sudo systemctl stop daphne
sudo systemctl disable daphne

# Re-enable when needed
sudo systemctl enable daphne
sudo systemctl start daphne
```

### Option 3: Use Redis with Smaller Memory Limit
Edit `/etc/redis/redis.conf`:
```
maxmemory 30mb
maxmemory-policy allkeys-lru
```

## Troubleshooting

### If Still Slow After Fix
```bash
# Check what's using CPU
top -o %CPU

# Check what's using memory
top -o %MEM

# Check for errors
sudo tail -f /var/log/nginx/error.log
sudo journalctl -u gunicorn -f
```

### If Gunicorn Won't Start
```bash
# Check logs
sudo journalctl -u gunicorn -n 100 --no-pager

# Test manually
cd /var/www/scan2food/application/scan2food
source venv/bin/activate
gunicorn --workers 2 --bind 127.0.0.1:8000 theatreApp.wsgi:application
```

### Rollback If Needed
```bash
# Restore backup
sudo cp /etc/systemd/system/gunicorn.service.backup /etc/systemd/system/gunicorn.service
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
```

## Summary
- **Before**: 4 workers, 66MB free RAM, 100% CPU, very slow
- **After**: 2 workers, ~250MB free RAM, normal CPU, fast
- **Trade-off**: Slightly less concurrent request handling (still sufficient for your traffic)
- **Benefit**: Website is fast and stable again
