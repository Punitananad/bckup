# WebSocket Issues - Root Cause Analysis

## Summary
The WebSocket connections are being rejected, but NOT because of browser caching. The actual issues are:

1. **Nginx Static Path Mismatch** (CRITICAL)
2. **Weak Security Model** (API keys in JavaScript)
3. **Consumer Lifecycle Issues** (Fixed)

---

## Issue 1: Nginx Static Path Mismatch ⚠️ CRITICAL

### The Problem
```
Django STATIC_ROOT:  /var/www/scan2food/static
Nginx serves from:   /var/www/scan2food/staticfiles  ❌ WRONG
```

### Evidence
```bash
# File exists on disk with API key
$ grep "05XnhaghUWM6Hd7YVR6" /var/www/scan2food/static/theatre_js/live-orders/worker.js
✓ Found

# But Nginx serves from wrong directory
$ curl https://calculatentrade.com/static/theatre_js/live-orders/worker.js | grep "ws_key"
❌ Not found
```

### Why This Happens
- `collectstatic` puts files in `/var/www/scan2food/static`
- Nginx is configured to serve from `/var/www/scan2food/staticfiles`
- These are DIFFERENT directories
- Nginx is serving old/cached files from the wrong location

### The Fix
```bash
# 1. Backup current config
sudo cp /etc/nginx/sites-available/scan2food /etc/nginx/sites-available/scan2food.backup

# 2. Fix the path
sudo sed -i 's|/var/www/scan2food/staticfiles/|/var/www/scan2food/static/|g' /etc/nginx/sites-available/scan2food

# 3. Test and restart
sudo nginx -t
sudo systemctl restart nginx

# 4. Verify
curl -s https://calculatentrade.com/static/theatre_js/live-orders/worker.js | grep "05XnhaghUWM6Hd7YVR6"
# Should now show the API key
```

---

## Issue 2: Weak Security Model 🔒

### The Problem
API keys are hardcoded in JavaScript files:
```javascript
const ws_key = "05XnhaghUWM6Hd7YVR6_iPcJGfH_YDn3RiDv1Rh-zNM";
const ws_url = `wss://${window.location.host}/ws/all-seat-datasocket/?key=${ws_key}`;
```

### Why This Is Bad
1. Anyone can open DevTools and see the key
2. Key can be copied and used from anywhere
3. No per-user tracking
4. Can't revoke access without changing key everywhere
5. Shared key across all users

### Better Solution: Session Authentication
```python
# Consumer checks Django session instead of API key
class AllSeatConsumers(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user')
        
        if not user.is_authenticated:
            await self.close()
            return
        
        # User is logged in - allow connection
        self.group_name = "all-seat-status"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
```

```javascript
// Frontend - no API key needed!
const ws_url = `wss://${window.location.host}/ws/all-seat-datasocket/`;
const socket = new WebSocket(ws_url);
// Session cookie is automatically sent
```

### Benefits
- ✅ No keys in frontend
- ✅ Uses existing Django auth
- ✅ Per-user sessions
- ✅ Can add role-based permissions
- ✅ httpOnly cookies (can't be stolen)

---

## Issue 3: Consumer Lifecycle (FIXED ✓)

### The Problem (Was)
```python
async def disconnect(self, code):
    # This crashed if connection was rejected before accept()
    await self.channel_layer.group_discard(
        self.group_name,  # ❌ AttributeError if connect() rejected early
        self.channel_name
    )
```

### The Fix (Already Applied)
```python
async def disconnect(self, code):
    # Only discard if group_name was set (connection was accepted)
    if hasattr(self, 'group_name'):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
```

This is already fixed in all three consumers.

---

## What's NOT The Problem

### ❌ Browser Caching
- Browser cache doesn't matter if Nginx serves wrong files
- Version parameters (`?v=20260211001`) are useless if Nginx path is wrong

### ❌ collectstatic
- `collectstatic` is working correctly
- Files ARE in `/var/www/scan2food/static`
- The problem is Nginx looking in the wrong place

### ❌ Consumer Code
- Consumer logic is correct
- Key validation works
- Lifecycle is fixed

---

## Current Status

### What's Working ✓
- Consumer code has proper key validation
- Consumer lifecycle (connect/disconnect) is fixed
- Static files are collected correctly
- API keys are in the files on disk

### What's Broken ❌
- Nginx serves from wrong directory
- API keys not reaching browser
- WebSocket connections rejected (no key in URL)

---

## Fix Priority

### 1. IMMEDIATE (Do Now)
Fix Nginx static path mismatch
```bash
bash CRITICAL_FIXES_RUN_NOW.sh
```

### 2. SHORT TERM (This Week)
Migrate to session-based authentication
- Remove API keys from JavaScript
- Use Django session auth
- Add permission checks

### 3. LONG TERM (Next Sprint)
- Add rate limiting
- Add connection monitoring
- Add WebSocket metrics

---

## Verification Steps

After fixing Nginx path:

1. **Check file on disk:**
   ```bash
   grep "05XnhaghUWM6Hd7YVR6" /var/www/scan2food/static/theatre_js/live-orders/worker.js
   ```
   Should show: ✓ Found

2. **Check what Nginx serves:**
   ```bash
   curl -s https://calculatentrade.com/static/theatre_js/live-orders/worker.js | grep "05XnhaghUWM6Hd7YVR6"
   ```
   Should show: ✓ Found (after fix)

3. **Check browser console:**
   - Open DevTools → Network tab
   - Look for WebSocket connection
   - URL should be: `wss://calculatentrade.com/ws/all-seat-datasocket/?key=05XnhaghUWM6Hd7YVR6_iPcJGfH_YDn3RiDv1Rh-zNM`

4. **Check Daphne logs:**
   ```bash
   sudo journalctl -u daphne -f
   ```
   Should see: `WSCONNECT` instead of `WSREJECT`

---

## Commands to Run on Server

```bash
# 1. Navigate to project
cd /var/www/scan2food

# 2. Run the fix script
bash CRITICAL_FIXES_RUN_NOW.sh

# 3. Monitor logs
sudo journalctl -u daphne -f

# 4. Test in browser (hard refresh)
# Ctrl + Shift + R
```

---

## Conclusion

The root cause is **Nginx serving from the wrong directory**, not browser caching or collectstatic issues.

Once the Nginx path is fixed, the API keys will reach the browser and WebSocket connections will work.

However, the API key approach is still weak security. After confirming WebSockets work, migrate to session-based authentication for proper security.
