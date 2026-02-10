# WebSocket Fix - Execute These Commands

## Problem Identified
The CHANNEL_LAYERS in settings.py was configured to use Redis, but Redis is disabled. This causes WebSocket connections to fail.

## Solution
Switch CHANNEL_LAYERS to use InMemoryChannelLayer instead of Redis.

## Execute on Server

### Step 1: Navigate to project and pull changes
```bash
cd /var/www/scan2food
git stash
git pull origin main
git stash pop
```

### Step 2: Verify the fix in settings.py
```bash
cd application/scan2food
source venv/bin/activate
grep -A 5 "CHANNEL_LAYERS" theatreApp/settings.py
```

**Expected output should show:**
```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    },
}
```

### Step 3: Restart all services
```bash
sudo systemctl restart daphne
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### Step 4: Verify services are running
```bash
# Check Daphne
sudo systemctl status daphne

# Check port 8001
sudo ss -tlnp | grep 8001

# Should show something like:
# LISTEN 0  128  127.0.0.1:8001  0.0.0.0:*  users:(("daphne",pid=XXXX,fd=X))
```

### Step 5: Test WebSocket endpoint
```bash
# Test Daphne directly
curl -I http://127.0.0.1:8001/ws/all-seat-datasocket/

# Should return HTTP 200 or 101 (not 404)
```

### Step 6: Test in browser
1. Open https://calculatentrade.com
2. Open browser console (F12)
3. Run this command:
```javascript
const ws = new WebSocket('wss://calculatentrade.com/ws/all-seat-datasocket/');
ws.onopen = () => console.log('✓ Connected!');
ws.onerror = (e) => console.error('✗ Error:', e);
```

**Expected:** You should see "✓ Connected!" in console

## If Issues Persist

### Check Daphne logs
```bash
sudo journalctl -u daphne -n 50 --no-pager
```

### Check Nginx logs
```bash
sudo tail -20 /var/log/nginx/error.log
```

### Restart everything
```bash
sudo systemctl restart daphne gunicorn nginx
```

## What Changed

### Before (BROKEN):
```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",  # ❌ Redis disabled
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
```

### After (FIXED):
```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"  # ✅ Works without Redis
    },
}
```

## Important Notes

1. **InMemoryChannelLayer** works for single-server deployments
2. If you scale to multiple servers, you'll need to enable Redis
3. All WebSocket routes start with `/ws/`
4. Daphne handles WebSocket on port 8001
5. Nginx proxies WebSocket traffic to Daphne

## Success Indicators

✅ Daphne service running: `sudo systemctl is-active daphne` returns "active"
✅ Port 8001 listening: `sudo ss -tlnp | grep 8001` shows daphne
✅ WebSocket connects: Browser console shows "Connected!"
✅ No Redis errors: `sudo journalctl -u daphne -n 20` shows no Redis connection errors

## Quick Diagnostic Script

Run this to check everything:
```bash
cd /var/www/scan2food
bash check_websocket_config.sh
```

Or use the automated deployment:
```bash
cd /var/www/scan2food
bash deploy_websocket_fix.sh
```
