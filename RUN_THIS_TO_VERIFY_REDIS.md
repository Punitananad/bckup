# Quick Verification - Is Redis Working?

## Run These Commands on Server

```bash
# 1. Go to project directory
cd /var/www/scan2food

# 2. Make script executable
chmod +x verify_redis_working.py

# 3. Run verification
python3 verify_redis_working.py
```

## What You Should See

### ✅ If Redis is Working:
```
✅ SUCCESS: Using RedisChannelLayer
✅ Message sent successfully!
RESULT: Redis channel layer is working correctly!
```

### ❌ If Still Using InMemory:
```
❌ PROBLEM: Still using InMemoryChannelLayer
```

---

## If Redis is Working But Live Orders Still Don't Update

Then the problem is somewhere else. Check:

### 1. Browser Console (F12)
- Open live orders page
- Press F12 → Console tab
- Look for WebSocket errors
- Should see: `WebSocket connection established`

### 2. Check Daphne Logs
```bash
sudo journalctl -u daphne -f
```
- Create a test order
- Watch for messages in logs

### 3. Check Redis is Running
```bash
redis-cli ping
# Should return: PONG

sudo systemctl status redis-server
# Should show: active (running)
```

### 4. Restart Services (if needed)
```bash
sudo systemctl restart redis-server
sudo systemctl restart gunicorn
sudo systemctl restart daphne

# Wait 5 seconds, then test again
```

---

## Quick Test After Verification

1. Open live orders page: `https://calculatentrade.com/live-orders/`
2. Open another browser/incognito window
3. Create a test order
4. Order should appear **instantly** on live orders page (no refresh!)

---

## If Nothing Works

Run the full diagnostic:
```bash
cd /var/www/scan2food
chmod +x diagnose_redis_websocket.sh
./diagnose_redis_websocket.sh
```

Send me the output and I'll help debug further.
