# Live Orders Not Updating - Complete Diagnostic Guide

## Current Status

✅ Redis is configured in settings.py  
✅ Chat WebSocket works (proves WebSocket infrastructure is working)  
❌ Live orders don't update without refresh  

## The Flow (How It Should Work)

```
1. Customer creates order → Gunicorn worker processes request
2. Order saved to database
3. update_websocket() called → Sends message to Redis
4. Redis forwards message → Daphne receives it
5. Daphne sends to WebSocket clients → Browser receives update
6. JavaScript worker.js processes message → UI updates instantly
```

## Step-by-Step Verification

### Step 1: Verify Redis is Active

Run this on server:
```bash
cd /var/www/scan2food
python3 verify_redis_working.py
```

**Expected Output:**
```
✅ SUCCESS: Using RedisChannelLayer
✅ Message sent successfully!
```

**If you see "InMemoryChannelLayer":**
- Settings.py change didn't take effect
- Services need restart: `sudo systemctl restart gunicorn daphne`

---

### Step 2: Check Services Are Running

```bash
# Check all services
sudo systemctl status redis-server gunicorn daphne nginx

# All should show: active (running)
```

**If any service is not running:**
```bash
sudo systemctl restart redis-server
sudo systemctl restart gunicorn
sudo systemctl restart daphne
```

---

### Step 3: Test Redis Connection

```bash
redis-cli ping
```

**Expected:** `PONG`

**If you get error:**
```bash
# Check Redis logs
sudo journalctl -u redis-server -n 50

# Restart Redis
sudo systemctl restart redis-server
```

---

### Step 4: Monitor Daphne Logs (Real-Time)

Open a terminal and run:
```bash
sudo journalctl -u daphne -f
```

Keep this running and create a test order from another browser.

**What to look for:**
- WebSocket connection messages
- Any errors or exceptions
- Messages being received from Redis

---

### Step 5: Check Browser Console

1. Open live orders page: `https://calculatentrade.com/live-orders/`
2. Press F12 → Console tab
3. Look for:
   - `WebSocket connection established` (good)
   - Any WebSocket errors (bad)
   - Connection refused errors (bad)

**Common Issues:**
- `WebSocket connection failed` → Daphne not running
- `Connection refused` → Nginx not forwarding WebSocket
- No errors but no updates → Redis not working

---

### Step 6: Test WebSocket Connection

In browser console (F12), run:
```javascript
// Check if WebSocket is connected
console.log("Testing WebSocket...");

// This should show WebSocket status
```

---

### Step 7: Create Test Order

1. Keep live orders page open
2. Open another browser/incognito window
3. Go to customer order page
4. Create a test order
5. **Order should appear INSTANTLY on live orders page**

**If order doesn't appear:**
- Check Daphne logs (Step 4)
- Check browser console (Step 5)
- Verify Redis is working (Step 1)

---

## Common Problems & Solutions

### Problem 1: Redis Not Active
**Symptom:** verify_redis_working.py shows "InMemoryChannelLayer"

**Solution:**
```bash
# 1. Verify settings.py has Redis config
cd /var/www/scan2food/application/scan2food
cat theatreApp/settings.py | grep -A 10 "CHANNEL_LAYERS"

# Should show: "channels_redis.core.RedisChannelLayer"

# 2. Restart services
sudo systemctl restart gunicorn daphne

# 3. Wait 10 seconds, then test again
sleep 10
python3 /var/www/scan2food/verify_redis_working.py
```

---

### Problem 2: Redis Authentication Error
**Symptom:** `(error) NOAUTH Authentication required`

**Solution:**
```bash
# Remove password requirement
sudo nano /etc/redis/redis.conf

# Find and comment out (add # at start):
# requirepass your_password

# Save and restart
sudo systemctl restart redis-server

# Test
redis-cli ping
# Should return: PONG
```

---

### Problem 3: Daphne Not Running
**Symptom:** WebSocket connection refused in browser

**Solution:**
```bash
# Check Daphne status
sudo systemctl status daphne

# If not running, start it
sudo systemctl start daphne

# Check logs for errors
sudo journalctl -u daphne -n 50
```

---

### Problem 4: WebSocket Connects But No Updates
**Symptom:** WebSocket connected, but orders don't appear

**Possible Causes:**
1. Redis not forwarding messages
2. update_websocket() not being called
3. JavaScript not processing messages

**Solution:**
```bash
# 1. Monitor Redis activity
redis-cli MONITOR

# 2. Create test order
# 3. You should see Redis activity

# If no Redis activity:
# - update_websocket() might not be called
# - Check where orders are created in code
```

---

### Problem 5: Orders Appear After Long Delay
**Symptom:** Orders appear but after 30-60 seconds

**Possible Cause:** Cache timeout issue

**Solution:**
Check cache configuration in settings.py:
```python
# Should be using DummyCache or Redis, not InMemory
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}
```

---

## Quick Fix Commands

If nothing works, run these in order:

```bash
# 1. Go to project
cd /var/www/scan2food/application/scan2food

# 2. Activate venv
source venv/bin/activate

# 3. Verify Redis config
python3 /var/www/scan2food/verify_redis_working.py

# 4. Restart everything
sudo systemctl restart redis-server
sudo systemctl restart gunicorn
sudo systemctl restart daphne

# 5. Wait 10 seconds
sleep 10

# 6. Check services
sudo systemctl status redis-server gunicorn daphne

# 7. Test Redis
redis-cli ping

# 8. Monitor Daphne
sudo journalctl -u daphne -f
```

---

## What to Send Me If Still Not Working

If after all these steps it still doesn't work, send me:

1. **Output of verification script:**
   ```bash
   python3 /var/www/scan2food/verify_redis_working.py
   ```

2. **Service status:**
   ```bash
   sudo systemctl status redis-server gunicorn daphne
   ```

3. **Daphne logs when creating order:**
   ```bash
   # Keep this running, create order, copy output
   sudo journalctl -u daphne -f
   ```

4. **Browser console errors:**
   - Open F12 → Console
   - Screenshot any errors

5. **Redis monitor output:**
   ```bash
   # Run this, create order, copy output
   timeout 10 redis-cli MONITOR
   ```

---

## Expected Behavior After Fix

✅ Open live orders page  
✅ Create order from another browser  
✅ Order appears **INSTANTLY** (within 1 second)  
✅ No page refresh needed  
✅ Sound plays when order arrives  
✅ Notification shows "New Order"  

---

## Memory Usage

After enabling Redis:
- Redis: ~30-50MB
- Gunicorn (2 workers): ~200MB
- Daphne: ~100MB
- Total: ~350MB used
- Free: ~300MB (healthy!)

Your server has enough RAM for this setup.
