# Static Files Issue - Diagnosis and Fix

## Root Cause
You're accessing the site via `calculatentrade.com` (production server), but the static files aren't being served correctly on that server.

The error `net::ERR_UNKNOWN_URL_SCHEME` means the browser is trying to load resources with an invalid or missing URL scheme.

## Two Scenarios

### Scenario 1: Testing Locally
If you want to test locally:

1. **Stop accessing via `calculatentrade.com`**
2. **Run the local server:**
   ```bash
   run_local.bat
   ```
3. **Access via:**
   ```
   http://localhost:8000/theatre/live-orders/
   ```

### Scenario 2: Fix Production Server
If you need to fix the production server at `calculatentrade.com`:

#### Check 1: Nginx Configuration
The static files need to be served by Nginx. Check `/etc/nginx/sites-available/scan2food`:

```nginx
location /static/ {
    alias /var/www/scan2food/static/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}

location /media/ {
    alias /path/to/your/media/;
}
```

#### Check 2: Collect Static Files on Server
SSH into the production server and run:

```bash
cd /path/to/your/application/scan2food
source /path/to/venv/bin/activate
python manage.py collectstatic --noinput
```

This will copy all static files to `/var/www/scan2food/static/`

#### Check 3: Verify Static Files Exist on Server
```bash
ls -la /var/www/scan2food/static/
```

Should show directories like:
- assets/
- theatre_js/
- admin/
- etc.

#### Check 4: Restart Nginx
```bash
sudo systemctl restart nginx
```

#### Check 5: Test Static File Access
Try accessing directly:
```
https://calculatentrade.com/static/assets/css/style.css
```

If you get a 404, the Nginx configuration is wrong or files aren't collected.

## Quick Production Fix Script

Create this script on your production server:

```bash
#!/bin/bash
# fix_static_files.sh

echo "Collecting static files..."
cd /path/to/application/scan2food
source /path/to/venv/bin/activate
python manage.py collectstatic --noinput

echo "Setting permissions..."
sudo chown -R www-data:www-data /var/www/scan2food/static/
sudo chmod -R 755 /var/www/scan2food/static/

echo "Restarting Nginx..."
sudo systemctl restart nginx

echo "Done! Test your site now."
```

## Immediate Action Required

**Determine which environment you're working in:**

1. **Local Development** → Use `http://localhost:8000`
2. **Production Server** → Fix static files collection and Nginx config

The error you're seeing is because the production server isn't serving static files correctly.
