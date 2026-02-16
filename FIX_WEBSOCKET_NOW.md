# 🔧 FIX WEBSOCKET CONNECTION - QUICK GUIDE

**Issue:** WebSocket connections returning 404 errors  
**Cause:** Redis password not configured in CHANNEL_LAYERS

---

## 🚀 QUICK FIX (Run on Server)

### Step 1: SSH into Server
```bash
ssh root@165.22.219.111
```

### Step 2: Update Django Settings
```bash
cd /var/www/scan2food/application/scan2food

# Backup settings file
cp theatreApp/settings.py theatreApp/settings.py.backup_websocket

# Edit settings.py
nano theatreApp/settings.py
```

### Step 3: Find and Replace CHANNEL_LAYERS Configuration

Find this section (around line 108):
```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
```

Replace it with:
```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": ["redis://:scann2Food@127.0.0.1:6379/0"],
        },
    },
}
```

Save and exit (Ctrl+X, then Y, then Enter)

### Step 4: Restart Services
```bash
# Restart Daphne (WebSocket server)
sudo systemctl restart daphne

# Wait a moment
sleep 3

# Check Daphne status
sudo systemctl status daphne

# Restart Gunicorn
sudo systemctl restart gunicorn

# Restart Nginx
sudo systemctl restart nginx
```

### Step 5: Test WebSocket Connection
```bash
# Test the WebSocket endpoint
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: test" \
  https://scan2food.com/ws/all-seat-datasocket/
```

You should see HTTP 101 Switching Protocols (not 404)

---

## ✅ VERIFICATION

### Check Browser Console
1. Open https://scan2food.com/admin-portal/ in browser
2. Open Developer Tools (F12)
3. Go to Console tab
4. Look for WebSocket connection messages
5. Should see: "WebSocket connection established" (not errors)

### Check Server Logs
```bash
# Monitor Daphne logs in real-time
sudo journalctl -u daphne -f

# In another terminal, refresh the browser page
# You should see WebSocket connection logs
```

---

## 🔍 TROUBLESHOOTING

### If Still Getting 404 Errors

Check if Redis is running:
```bash
sudo systemctl status redis
redis-cli -a scann2Food PING
```

Should return: PONG

### If Redis Not Running
```bash
sudo systemctl start redis
sudo systemctl enable redis
```

### Check Daphne Logs for Errors
```bash
sudo journalctl -u daphne -n 50 --no-pager
```

Look for:
- Redis connection errors
- Import errors
- Consumer errors

### Verify Channels Redis Package
```bash
cd /var/www/scan2food/application/scan2food
source venv/bin/activate
pip show channels-redis
```

If not installed:
```bash
pip install channels-redis
sudo systemctl restart daphne
```

---

## 📊 EXPECTED RESULTS

### Before Fix:
```
❌ WebSocket connection to 'wss://scan2food.com/ws/all-seat-datasocket/' failed
❌ HTTP 404 Not Found
❌ Console errors in browser
```

### After Fix:
```
✅ WebSocket connection established
✅ HTTP 101 Switching Protocols
✅ No console errors
✅ Live updates working
```

---

## 🎯 WHAT THIS FIXES

1. WebSocket 404 errors
2. Live order updates not working
3. Real-time seat status not updating
4. Chat socket connection failures

---

**Last Updated:** February 17, 2026
