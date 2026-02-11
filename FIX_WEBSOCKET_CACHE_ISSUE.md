# Fix WebSocket Connection Issue - Browser Cache Problem

## Problem:
WebSocket connections failing because browser is loading OLD JavaScript files without API keys.

Error shows: `wss://calculatentrade.com/ws/all-seat-datasocket/`
Should be: `wss://calculatentrade.com/ws/all-seat-datasocket/?key=05XnhaghUWM6Hd7YVR6_iPcJGfH_YDn3RiDv1Rh-zNM`

## Root Cause:
The updated JavaScript files with API keys are in the repository, but:
1. Static files not collected on server yet
2. Browser is caching old JavaScript files
3. Nginx might be caching static files

## Solution - Run on Server:

```bash
cd /var/www/scan2food

# Pull latest code
git pull origin main

# Activate virtual environment
source application/scan2food/venv/bin/activate

# Go to Django app directory
cd application/scan2food

# Add WebSocket keys to .env if not already there
nano .env
# Add these lines:
# LIVE_ORDERS_WS_KEY=05XnhaghUWM6Hd7YVR6_iPcJGfH_YDn3RiDv1Rh-zNM
# PAYMENT_STATUS_WS_KEY=vy8ALNb9ev6DvTFGHv9IC3RgQ0xL5shqNmnFmDEHNqM
# CHAT_WS_KEY=A0B9sna1Pdio-1MdXHG8kQJwuC_45Ok2ZmlQbS_0B-U

# CRITICAL: Collect static files (this copies JavaScript with API keys)
python manage.py collectstatic --noinput --clear

# Restart services
sudo systemctl restart daphne
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# Verify Daphne is running
sudo systemctl status daphne
```

## After Server Deployment:

### Clear Browser Cache:
1. **Hard Refresh**: Press `Ctrl + Shift + R` (or `Cmd + Shift + R` on Mac)
2. **Or Clear Cache**: 
   - Open DevTools (F12)
   - Right-click refresh button
   - Select "Empty Cache and Hard Reload"

### Verify JavaScript is Updated:
1. Open DevTools (F12)
2. Go to Sources tab
3. Find: `static/theatre_js/live-orders/worker.js`
4. Search for: `05XnhaghUWM6Hd7YVR6`
5. Should see: `const ws_key = '05XnhaghUWM6Hd7YVR6_iPcJGfH_YDn3RiDv1Rh-zNM';`

### Check WebSocket Connection:
1. Open DevTools (F12)
2. Go to Network tab
3. Filter by "WS"
4. Should see: `all-seat-datasocket/?key=05XnhaghUWM6Hd7YVR6_iPcJGfH_YDn3RiDv1Rh-zNM`
5. Status should be: `101 Switching Protocols` (success)

## If Still Not Working:

### Check Daphne Logs:
```bash
sudo journalctl -u daphne -f
```

### Check if .env keys are loaded:
```bash
cd /var/www/scan2food/application/scan2food
source venv/bin/activate
python manage.py shell
```
Then in Python shell:
```python
from django.conf import settings
print(settings.LIVE_ORDERS_WS_KEY)
# Should print: 05XnhaghUWM6Hd7YVR6_iPcJGfH_YDn3RiDv1Rh-zNM
```

### Check static files location:
```bash
ls -la /var/www/scan2food/static/theatre_js/live-orders/worker.js
cat /var/www/scan2food/static/theatre_js/live-orders/worker.js | grep "ws_key"
# Should show: const ws_key = '05XnhaghUWM6Hd7YVR6_iPcJGfH_YDn3RiDv1Rh-zNM';
```

## Important Notes:

1. **DO NOT remove security** - The security code is correct
2. **Problem is cache** - Browser and server are serving old files
3. **collectstatic is critical** - This copies updated JavaScript to /var/www/scan2food/static/
4. **Hard refresh required** - Browser must reload JavaScript files

## Summary:

The WebSocket security is working correctly. The issue is that:
- Updated JavaScript files (with API keys) exist in repository
- But they haven't been deployed to the server's static files directory
- And browser is caching the old JavaScript files

Running `collectstatic` and hard refreshing the browser will fix it.
