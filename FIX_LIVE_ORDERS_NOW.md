# Fix Live Orders - Run These Commands

## Quick Summary

You already changed settings.py to use Redis. Now we need to verify it's working.

---

## Step 1: Verify Redis is Active

```bash
cd /var/www/scan2food
python3 verify_redis_working.py
```

### What You Should See:

✅ **If Working:**
```
✅ SUCCESS: Using RedisChannelLayer
✅ Message sent successfully!
```
→ Go to Step 2

❌ **If Not Working:**
```
❌ PROBLEM: Still using InMemoryChannelLayer
```
→ Run these commands:
```bash
sudo systemctl restart gunicorn
sudo systemctl restart daphne
sleep 10
python3 verify_redis_working.py
```

---

## Step 2: Test WebSocket Flow

```bash
python3 test_websocket_flow.py
```

This sends a test order through the WebSocket system.

### What to Do:

1. **Before running:** Open live orders page in browser
   - URL: `https://calculatentrade.com/live-orders/`
   - Keep it open

2. **Run the script:** `python3 test_websocket_flow.py`

3. **Check browser:** Test order should appear instantly
   - Theatre ID: 31
   - Seat: "Test Hall | Test Seat"
   - Order ID: TEST-12345

4. **If test order appears:** ✅ Everything is working!

5. **If test order does NOT appear:** Go to Step 3

---

## Step 3: Check Browser Console

1. Open live orders page
2. Press **F12** (opens developer tools)
3. Click **Console** tab
4. Look for errors

### Common Errors:

**"WebSocket connection failed"**
→ Daphne not running
```bash
sudo systemctl restart daphne
```

**"Connection refused"**
→ Nginx not forwarding WebSocket
```bash
sudo systemctl restart nginx
```

**No errors but no updates**
→ Redis not forwarding messages
```bash
sudo systemctl restart redis-server
sudo systemctl restart daphne
```

---

## Step 4: Monitor Daphne Logs

Open a new terminal and run:
```bash
sudo journalctl -u daphne -f
```

Keep this running and create a test order.

**What to look for:**
- Messages being received
- Any errors or exceptions
- WebSocket activity

---

## Step 5: Create Real Test Order

1. Keep live orders page open
2. Open another browser (or incognito window)
3. Go to customer order page
4. Create a real order
5. **Order should appear INSTANTLY on live orders page**

---

## If Still Not Working

Run the full diagnostic:
```bash
cd /var/www/scan2food
chmod +x diagnose_redis_websocket.sh
./diagnose_redis_websocket.sh > diagnostic_output.txt
```

Then send me the `diagnostic_output.txt` file.

---

## Quick Restart All Services

If you want to restart everything:
```bash
sudo systemctl restart redis-server
sudo systemctl restart gunicorn
sudo systemctl restart daphne
sleep 10
echo "Services restarted. Test now."
```

---

## What Should Happen When Working

✅ Customer creates order  
✅ Order appears on live orders page **instantly** (within 1 second)  
✅ Sound plays  
✅ Notification shows "New Order"  
✅ No page refresh needed  

---

## Memory Check

After enabling Redis, check memory:
```bash
free -h
```

You should have ~300MB free (which is healthy).

---

## Files Created for You

1. **verify_redis_working.py** - Check if Redis is active
2. **test_websocket_flow.py** - Test WebSocket message flow
3. **LIVE_ORDERS_DIAGNOSTIC.md** - Complete diagnostic guide
4. **RUN_THIS_TO_VERIFY_REDIS.md** - Quick verification guide

---

## Summary

The fix is already done (Redis configured in settings.py).

Now just:
1. Verify Redis is active
2. Test WebSocket flow
3. Create real order
4. Should work instantly!

If it doesn't work after Step 1, send me the output and I'll help debug.
