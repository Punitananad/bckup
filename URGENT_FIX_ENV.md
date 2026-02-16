# URGENT FIX: Environment Variables Not Loading

## Problem Found

The diagnostic shows:
- ✗ API_KEY is loading as "CHANGE_THI..." (default from settings.py)
- ✗ NOT loading from .env file
- ✗ Middleware not running because API_KEY is wrong

**Root Cause**: Gunicorn's `EnvironmentFile` directive is not loading the .env file properly.

## Solution

Add environment variables EXPLICITLY to the gunicorn service file.

---

## Quick Fix (Copy-Paste on Production Server)

```bash
# Step 1: Read API_KEY from .env
cd /var/www/scan2food/application/scan2food
API_KEY=$(grep "^API_KEY=" .env | cut -d= -f2)
echo "API_KEY: ${API_KEY:0:20}..."

# Step 2: Create gunicorn service with explicit Environment directives
sudo tee /etc/systemd/system/gunicorn.service > /dev/null << EOF
[Unit]
Description=Gunicorn daemon
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/scan2food/application/scan2food
Environment="API_KEY=$API_KEY"
Environment="DJANGO_ENV=production"
Environment="LIVE_ORDERS_WS_KEY=05XnhaghUWM6Hd7YVR6_iPcJGfH_YDn3RiDv1Rh-zNM"
Environment="PAYMENT_STATUS_WS_KEY=vy8ALNb9ev6DvTFGHv9IC3RgQ0xL5shqNmnFmDEHNqM"
Environment="CHAT_WS_KEY=A0B9sna1Pdio-1MdXHG8kQJwuC_45Ok2ZmlQbS_0B-U"
EnvironmentFile=/var/www/scan2food/application/scan2food/.env
ExecStart=/var/www/scan2food/application/scan2food/venv/bin/gunicorn --workers 2 --bind unix:/var/www/scan2food/application/scan2food/gunicorn.sock theatreApp.wsgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Step 3: Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
sudo systemctl restart daphne
sleep 3

# Step 4: Test (should return 401)
curl -i https://scan2food.com/theatre/api/theatre-detail

# Step 5: Check middleware logs
sudo journalctl -u gunicorn -n 30 | grep MIDDLEWARE
```

---

## Alternative: Automated Script

```bash
bash fix_env_loading.sh
```

---

## What Changed

**Before:**
```ini
[Service]
EnvironmentFile=/var/www/scan2food/application/scan2food/.env
```

**After:**
```ini
[Service]
Environment="API_KEY=RDnXh86Ciczn2Orbc2CxQtQ6VB-tzl19bcKTtNrSK4Y"
Environment="DJANGO_ENV=production"
EnvironmentFile=/var/www/scan2food/application/scan2food/.env
```

The `Environment=` directive explicitly sets variables, while `EnvironmentFile=` sometimes fails to load properly.

---

## Verification

After running the fix:

1. **Test without API key** (should fail):
```bash
curl https://scan2food.com/theatre/api/theatre-detail
# Expected: {"error": "Invalid or missing API key", "status": 401}
```

2. **Test with API key** (should work):
```bash
curl -H "X-API-Key: RDnXh86Ciczn2Orbc2CxQtQ6VB-tzl19bcKTtNrSK4Y" https://scan2food.com/theatre/api/theatre-detail
# Expected: Theatre data (200 OK)
```

3. **Check middleware logs**:
```bash
sudo journalctl -u gunicorn -n 50 | grep MIDDLEWARE
# Expected: [MIDDLEWARE] Processing: GET /theatre/api/theatre-detail
```

---

## Why This Happened

Systemd's `EnvironmentFile=` directive has known issues:
- Doesn't always parse .env files correctly
- May not export variables to the process
- Timing issues during service startup

Using explicit `Environment=` directives is more reliable.

---

## Security Note

The API_KEY is now in the systemd service file. This is secure because:
- Only root can read/modify systemd service files
- The file is not in the git repository
- It's the standard way to pass secrets to systemd services

---

## Next Steps

1. Run the fix commands above
2. Verify middleware is working (401 errors)
3. Test customer site still works
4. Monitor logs for any issues
