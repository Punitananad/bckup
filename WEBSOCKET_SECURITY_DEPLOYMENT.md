# WebSocket Security Deployment Guide

## Problem Identified
The browser was caching JavaScript files even though the files on disk had the API keys. The HTML templates were loading JavaScript files with a static version parameter (`?v=20260211`) which didn't change, so browsers kept using cached versions.

## Solution Applied
Updated the version parameter in HTML templates from `?v=20260211` to `?v=20260211001` to force browsers to reload the JavaScript files.

## Files Modified
1. `application/scan2food/theatre/templates/theatre/live-orders.html` - Updated version to 20260211001
2. `application/scan2food/theatre/templates/theatre/all_seats.html` - Updated version to 20260211001

## Deployment Steps

### Option 1: Automated Deployment (Recommended)
```bash
cd /var/www/scan2food
bash deploy_websocket_security.sh
```

### Option 2: Manual Deployment
```bash
# 1. Navigate to project
cd /var/www/scan2food

# 2. Pull latest code
git pull origin main

# 3. Navigate to Django directory
cd application/scan2food
source venv/bin/activate

# 4. Remove old static files
rm -rf /var/www/scan2food/static/theatre_js/live-orders/
rm -rf /var/www/scan2food/static/theatre_js/chat-box/
rm -rf /var/www/scan2food/static/theatre_js/all-seat-socket.js
rm -rf /var/www/scan2food/static/theatre_js/payment-socket.js
rm -rf /var/www/scan2food/static/dashboard/live-order.js
rm -rf /var/www/scan2food/static/dashboard/chat-box/
rm -rf /var/www/scan2food/static/dashboard/profile/
rm -rf /var/www/scan2food/static/chatBox/

# 5. Collect static files
python manage.py collectstatic --noinput --clear

# 6. Restart services
sudo systemctl restart gunicorn
sudo systemctl restart daphne
sudo systemctl restart nginx

# 7. Verify
grep "05XnhaghUWM6Hd7YVR6" /var/www/scan2food/static/theatre_js/live-orders/worker.js
```

## Verification

### 1. Check Static Files
```bash
grep "05XnhaghUWM6Hd7YVR6" /var/www/scan2food/static/theatre_js/live-orders/worker.js
```
Should output: `const ws_key = '05XnhaghUWM6Hd7YVR6_iPcJGfH_YDn3RiDv1Rh-zNM';`

### 2. Check Daphne Logs
```bash
sudo journalctl -u daphne -f
```
Look for `WSCONNECT` messages instead of `WSREJECT`

### 3. Browser Testing
1. Open https://calculatentrade.com/theatre/live-orders in browser
2. Do a HARD REFRESH: **Ctrl+Shift+R** (Windows/Linux) or **Cmd+Shift+R** (Mac)
3. Open DevTools (F12) → Network tab
4. Look for WebSocket connection
5. Verify URL includes `?key=05XnhaghUWM6Hd7YVR6_iPcJGfH_YDn3RiDv1Rh-zNM`

### 4. Expected Results
- WebSocket URL should be: `wss://calculatentrade.com/ws/all-seat-datasocket/?key=05XnhaghUWM6Hd7YVR6_iPcJGfH_YDn3RiDv1Rh-zNM`
- Status should be: `101 Switching Protocols` (not 0)
- Daphne logs should show: `WSCONNECT` (not `WSREJECT`)

## Troubleshooting

### If WebSocket still fails after deployment:

1. **Clear browser cache completely**
   - Chrome: Settings → Privacy → Clear browsing data → Cached images and files
   - Or use Incognito mode

2. **Check if Nginx is caching**
   ```bash
   curl -I https://calculatentrade.com/static/theatre_js/live-orders/worker.js
   ```
   Look for `Cache-Control` headers

3. **Verify version parameter changed in HTML**
   ```bash
   curl -s https://calculatentrade.com/theatre/live-orders | grep "v=20260211001"
   ```
   Should find the new version number

4. **Check Daphne is running**
   ```bash
   sudo systemctl status daphne
   ```

## What Changed

### Before:
- HTML template: `<script src="{% static 'theatre_js/live-orders/main.js' %}?v=20260211"></script>`
- Browser cached this version
- Even though files on disk had API keys, browser used old cached version

### After:
- HTML template: `<script src="{% static 'theatre_js/live-orders/main.js' %}?v=20260211001"></script>`
- New version parameter forces browser to reload
- Browser gets fresh JavaScript with API keys

## Security Notes
- API keys are stored in `.env` file
- Keys are loaded via `settings.py`
- WebSocket consumers verify keys before accepting connections
- Invalid keys result in immediate disconnection

## Next Steps After Deployment
1. Monitor Daphne logs for successful connections
2. Test live orders page with real orders
3. Verify all 3 WebSocket endpoints work:
   - Live orders: `/ws/all-seat-datasocket/`
   - Payment status: `/ws/payment-status-socket/`
   - Chat: `/ws/chat/`
