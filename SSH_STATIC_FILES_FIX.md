# Fix Static Files on Production Server (SSH)

## Quick Fix - Run These Commands

### Step 1: Connect to Your Server
```bash
ssh root@calculatentrade.com
# or
ssh root@165.22.219.111
```

### Step 2: Run Diagnostic (Optional)
```bash
cd /root/application/scan2food
bash diagnose_static_files.sh
```

### Step 3: Fix Static Files
```bash
cd /root/application/scan2food
bash fix_production_static_files.sh
```

## Manual Fix (If Scripts Don't Work)

### 1. Activate Virtual Environment
```bash
source /root/venv/bin/activate
```

### 2. Navigate to Application
```bash
cd /root/application/scan2food
```

### 3. Collect Static Files
```bash
python manage.py collectstatic --noinput --clear
```

### 4. Set Permissions
```bash
sudo chown -R www-data:www-data /var/www/scan2food/static/
sudo chmod -R 755 /var/www/scan2food/static/
```

### 5. Check Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/scan2food
```

Make sure this block exists:
```nginx
location /static/ {
    alias /var/www/scan2food/static/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

### 6. Test Nginx Config
```bash
sudo nginx -t
```

### 7. Restart Services
```bash
sudo systemctl restart nginx
sudo systemctl restart gunicorn
sudo systemctl restart daphne
```

## Verify the Fix

### 1. Test Static File Access
Open in browser:
```
https://calculatentrade.com/static/assets/css/style.css
```

Should show CSS content, not a 404 error.

### 2. Check Your Page
```
https://calculatentrade.com/theatre/live-orders/
```

Open browser DevTools (F12) and check Console - no more `ERR_UNKNOWN_URL_SCHEME` errors.

### 3. Clear Browser Cache
Press `Ctrl + Shift + Delete` and clear cached images and files.

## Common Issues

### Issue 1: Permission Denied
```bash
sudo chown -R www-data:www-data /var/www/scan2food/
sudo chmod -R 755 /var/www/scan2food/
```

### Issue 2: Static Files Not Found
Check if STATIC_ROOT is correct in settings.py:
```bash
cd /root/application/scan2food
source /root/venv/bin/activate
python manage.py shell
```

Then in Python shell:
```python
from django.conf import settings
print(settings.STATIC_ROOT)
print(settings.STATIC_URL)
```

### Issue 3: Nginx Not Serving Static Files
Check Nginx error log:
```bash
sudo tail -f /var/log/nginx/error.log
```

### Issue 4: Files Collected But Still Not Loading
Restart all services:
```bash
sudo systemctl restart nginx gunicorn daphne
```

## Upload Scripts to Server

From your local machine, upload the fix scripts:

```bash
# Using SCP
scp fix_production_static_files.sh root@calculatentrade.com:/root/application/scan2food/
scp diagnose_static_files.sh root@calculatentrade.com:/root/application/scan2food/

# Make them executable
ssh root@calculatentrade.com "chmod +x /root/application/scan2food/*.sh"
```

Or manually copy the script content and create files on the server:
```bash
ssh root@calculatentrade.com
cd /root/application/scan2food
nano fix_production_static_files.sh
# Paste the script content
# Press Ctrl+X, then Y, then Enter
chmod +x fix_production_static_files.sh
```

## Quick One-Liner Fix

If you just want to run everything at once:
```bash
ssh root@calculatentrade.com "cd /root/application/scan2food && source /root/venv/bin/activate && python manage.py collectstatic --noinput --clear && sudo chown -R www-data:www-data /var/www/scan2food/static/ && sudo chmod -R 755 /var/www/scan2food/static/ && sudo systemctl restart nginx gunicorn daphne"
```

## After Fix

1. Clear browser cache
2. Hard refresh page (Ctrl + F5)
3. Check browser console (F12) - should be no errors
4. All CSS, JS, and images should load correctly
