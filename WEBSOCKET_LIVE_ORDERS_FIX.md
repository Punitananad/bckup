# Live Orders WebSocket Not Updating - Root Cause & Fix

## Problem

✅ **Chat WebSocket works** - Messages appear in real-time  
❌ **Live Orders WebSocket doesn't work** - Must refresh page to see new orders

## Root Cause

The issue is with **InMemoryChannelLayer** and how your application is structured:

### How It Works:
1. **Daphne** (port 8001) handles WebSocket connections
2. **Gunicorn** (socket file) handles HTTP requests (like creating orders)
3. When an order is created, `update_websocket()` is called from **Gunicorn worker**
4. `update_websocket()` sends message to channel layer
5. Channel layer should forward to **Daphne** → WebSocket clients

### The Problem:
**InMemoryChannelLayer** only works **within the same process**!

- Gunicorn workers (separate processes) ❌ Cannot communicate with Daphne (separate process)
- Messages sent from Gunicorn are lost - they never reach Daphne
- WebSocket clients connected to Daphne never receive updates

### Why Chat Works:
Chat likely works because messages are sent **from within Daphne** (WebSocket consumer), not from Gunicorn workers.

---

## Solution Options

### Option 1: Enable Redis (RECOMMENDED)

Redis allows **inter-process communication** between Gunicorn and Daphne.

**Pros:**
- ✅ Proper solution for production
- ✅ Works with multiple workers/servers
- ✅ Reliable and fast

**Cons:**
- ❌ Uses ~50MB RAM
- ❌ Requires Redis configuration

**How to implement:**

```bash
# 1. Install Redis (if not already installed)
sudo apt update
sudo apt install redis-server -y

# 2. Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# 3. Update Django settings
# Edit: application/scan2food/theatreApp/settings.py
```

Change CHANNEL_LAYERS to:
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

```bash
# 4. Restart services
sudo systemctl restart gunicorn daphne
```

---

### Option 2: Use Database Channel Layer (Alternative)

Uses database for inter-process communication (slower but no Redis needed).

**Pros:**
- ✅ No additional services
- ✅ No extra RAM usage

**Cons:**
- ❌ Slower than Redis
- ❌ More database load
- ❌ Not recommended for high traffic

**How to implement:**

```bash
# 1. Install channels-db
cd /var/www/scan2food/application/scan2food
source venv/bin/activate
pip install channels-db
```

```python
# 2. Update settings.py
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_db.core.DatabaseChannelLayer",
        "CONFIG": {
            "capacity": 100,
            "expiry": 60,
        },
    },
}

# 3. Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ... existing apps ...
    'channels_db',
]
```

```bash
# 4. Run migrations
python manage.py migrate

# 5. Restart services
sudo systemctl restart gunicorn daphne
```

---

### Option 3: Refactor to Send Updates from Daphne (Complex)

Move the `update_websocket()` calls to run within Daphne process instead of Gunicorn.

**Pros:**
- ✅ Works with InMemoryChannelLayer
- ✅ No Redis needed

**Cons:**
- ❌ Requires significant code refactoring
- ❌ Complex to implement
- ❌ Not recommended

---

## Recommended Solution: Enable Redis

Given your current setup, **enabling Redis is the best solution**:

1. **Minimal RAM impact**: Redis uses ~30-50MB (you have 347MB free now)
2. **Production-ready**: Proper solution for real-time features
3. **Easy to implement**: Just configuration changes
4. **Fast**: Much faster than database channel layer

---

## Step-by-Step Fix (Redis)

### 1. Check if Redis is installed:
```bash
redis-cli ping
```

If you get `PONG`, Redis is already installed!  
If you get `(error) NOAUTH Authentication required`, Redis needs configuration.

### 2. Configure Redis (if needed):
```bash
# Edit Redis config
sudo nano /etc/redis/redis.conf

# Find and comment out this line:
# requirepass your_password

# Or set a password and update Django settings accordingly

# Restart Redis
sudo systemctl restart redis-server
```

### 3. Update Django Settings:
```bash
cd /var/www/scan2food/application/scan2food
nano theatreApp/settings.py
```

Find the CHANNEL_LAYERS section and change to:
```python
# CHANNEL_LAYERS - Using Redis for inter-process communication
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
```

### 4. Restart Services:
```bash
sudo systemctl restart gunicorn daphne
```

### 5. Test:
1. Open live orders page
2. Create a new order from another browser/device
3. Order should appear **immediately** without refresh!

---

## Verification

After implementing the fix, verify it works:

```bash
# 1. Check Redis is running
sudo systemctl status redis-server

# 2. Check services are running
sudo systemctl status gunicorn daphne

# 3. Monitor Daphne logs
sudo journalctl -u daphne -f

# 4. Test creating an order
# - Open live orders page
# - Create order from another device
# - Should appear instantly!
```

---

## Memory Impact

**Before Redis:**
- Free: 347MB

**After Redis:**
- Redis: ~30-50MB
- Free: ~300MB (still healthy!)

With 2 Gunicorn workers, you have enough RAM for Redis.

---

## Why This Fixes It

```
BEFORE (InMemoryChannelLayer):
Order Created → Gunicorn Worker → InMemoryChannelLayer (lost!) ❌
                                                              ↓
                                                         Daphne (never receives)
                                                              ↓
                                                         WebSocket Client (no update)

AFTER (Redis):
Order Created → Gunicorn Worker → Redis → Daphne → WebSocket Client ✅
```

Redis acts as a **message broker** between processes, allowing Gunicorn workers to send messages that Daphne receives and forwards to WebSocket clients.

---

## Summary

**Problem**: InMemoryChannelLayer can't communicate between Gunicorn and Daphne  
**Solution**: Use Redis for inter-process communication  
**Impact**: ~30-50MB RAM, instant live updates  
**Difficulty**: Easy (just configuration changes)

Let me know if you want me to help implement this fix!
