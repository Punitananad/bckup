# Deploy Middleware Fix - Complete Guide

## Problem
The API key middleware is deployed but not intercepting requests. Possible causes:
1. Gunicorn service file has "kk" characters causing systemd warnings
2. Python bytecode cache not cleared
3. Middleware not being loaded properly

## Solution
This guide provides copy-paste commands to fix all issues.

---

## PART 1: Local Development (Push Changes)

Run these commands on your LOCAL machine:

```bash
# Navigate to project root
cd /path/to/scan2food

# Add all changes
git add .

# Commit with message
git commit -m "Fix: Add debug logging to middleware and fix deployment issues"

# Push to repository
git push origin main
```

---

## PART 2: Production Server (Pull and Deploy)

SSH into your production server and run these commands:

### Step 1: Pull Latest Code

```bash
# Navigate to project directory
cd /var/www/scan2food

# Pull latest changes
git pull origin main
```

### Step 2: Fix Gunicorn Service File

```bash
# Backup current service file
sudo cp /etc/systemd/system/gunicorn.service /etc/systemd/system/gunicorn.service.backup

# Create fixed service file (removes "kk" characters)
sudo tee /etc/systemd/system/gunicorn.service > /dev/null << 'EOF'
[Unit]
Description=Gunicorn daemon
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/scan2food/application/scan2food
EnvironmentFile=/var/www/scan2food/application/scan2food/.env
ExecStart=/var/www/scan2food/application/scan2food/venv/bin/gunicorn --workers 2 --bind unix:/var/www/scan2food/application/scan2food/gunicorn.sock theatreApp.wsgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload
```

### Step 3: Clear Python Cache

```bash
# Navigate to Django project
cd /var/www/scan2food/application/scan2food

# Clear all Python bytecode cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
```

### Step 4: Verify API Key in Environment

```bash
# Check if API_KEY is set
grep "API_KEY=" /var/www/scan2food/application/scan2food/.env

# Should show: API_KEY=RDnXh86Ciczn2Orbc2CxQtQ6VB-tzl19bcKTtNrSK4Y
```

### Step 5: Restart Services

```bash
# Restart Gunicorn
sudo systemctl restart gunicorn

# Restart Daphne
sudo systemctl restart daphne

# Wait 3 seconds for services to start
sleep 3
```

### Step 6: Check Service Status

```bash
# Check Gunicorn status
sudo systemctl status gunicorn --no-pager -l | head -20

# Check Daphne status
sudo systemctl status daphne --no-pager -l | head -20
```

### Step 7: View Middleware Logs

```bash
# View recent logs with middleware debug output
sudo journalctl -u gunicorn -n 100 | grep MIDDLEWARE

# If you see "[MIDDLEWARE]" logs, middleware is running!
```

---

## PART 3: Test Middleware

### Test from Server (using curl)

```bash
# Test 1: WITHOUT API key (should get 401 error)
curl -i https://scan2food.com/theatre/api/theatre-detail

# Expected: HTTP/1.1 401 Unauthorized
# Expected: {"error": "Invalid or missing API key", "status": 401}

# Test 2: WITH valid API key (should work)
curl -i -H "X-API-Key: RDnXh86Ciczn2Orbc2CxQtQ6VB-tzl19bcKTtNrSK4Y" https://scan2food.com/theatre/api/theatre-detail

# Expected: HTTP/1.1 200 OK
# Expected: JSON data with theatre details

# Test 3: WITH invalid API key (should get 401 error)
curl -i -H "X-API-Key: WRONG_KEY" https://scan2food.com/theatre/api/theatre-detail

# Expected: HTTP/1.1 401 Unauthorized
```

### Automated Test Script

```bash
# Make test script executable
chmod +x test_middleware_working.sh

# Run comprehensive tests
./test_middleware_working.sh
```

---

## PART 4: Verify Customer Site Still Works

1. Open browser to: https://scan2food.com/theatre/show-menu/1
2. Try to add items to cart
3. Try to place an order
4. Should work normally (JavaScript includes API key automatically)

---

## Troubleshooting

### If middleware still not working:

1. **Check if middleware is in settings.py:**
```bash
grep -A 10 "MIDDLEWARE = \[" /var/www/scan2food/application/scan2food/theatreApp/settings.py | grep APIKeyMiddleware
```

2. **Check for Python import errors:**
```bash
cd /var/www/scan2food/application/scan2food
source venv/bin/activate
python manage.py check
```

3. **Check Django can import middleware:**
```bash
cd /var/www/scan2food/application/scan2food
source venv/bin/activate
python -c "from theatreApp.middleware import APIKeyMiddleware; print('OK')"
```

4. **View full Gunicorn logs:**
```bash
sudo journalctl -u gunicorn -n 200 --no-pager
```

5. **Check if API_KEY is loaded in Django:**
```bash
cd /var/www/scan2food/application/scan2food
source venv/bin/activate
python manage.py shell << 'EOF'
from django.conf import settings
print(f"API_KEY loaded: {hasattr(settings, 'API_KEY')}")
print(f"API_KEY value: {settings.API_KEY[:10]}..." if hasattr(settings, 'API_KEY') else "NOT SET")
EOF
```

---

## Quick Copy-Paste Bundle (All Commands)

```bash
# === ON PRODUCTION SERVER ===

# Pull code
cd /var/www/scan2food && git pull origin main

# Fix gunicorn service
sudo tee /etc/systemd/system/gunicorn.service > /dev/null << 'EOF'
[Unit]
Description=Gunicorn daemon
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/scan2food/application/scan2food
EnvironmentFile=/var/www/scan2food/application/scan2food/.env
ExecStart=/var/www/scan2food/application/scan2food/venv/bin/gunicorn --workers 2 --bind unix:/var/www/scan2food/application/scan2food/gunicorn.sock theatreApp.wsgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Clear cache
cd /var/www/scan2food/application/scan2food && find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true && find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Restart services
sudo systemctl restart gunicorn && sudo systemctl restart daphne && sleep 3

# Check status
sudo systemctl status gunicorn --no-pager -l | head -20

# Test without API key (should fail)
curl -i https://scan2food.com/theatre/api/theatre-detail

# Test with API key (should work)
curl -i -H "X-API-Key: RDnXh86Ciczn2Orbc2CxQtQ6VB-tzl19bcKTtNrSK4Y" https://scan2food.com/theatre/api/theatre-detail

# View middleware logs
sudo journalctl -u gunicorn -n 50 | grep MIDDLEWARE
```

---

## Expected Results

After deployment:

✅ Requests WITHOUT API key → 401 Unauthorized  
✅ Requests WITH valid API key → 200 OK  
✅ Requests WITH invalid API key → 401 Unauthorized  
✅ Webhook endpoints → Work without API key  
✅ Customer ordering → Works normally (JavaScript has API key)  
✅ Middleware logs → Visible in journalctl  

---

## Security Notes

- API key is: `RDnXh86Ciczn2Orbc2CxQtQ6VB-tzl19bcKTtNrSK4Y`
- Stored in: `/var/www/scan2food/application/scan2food/.env`
- Injected into customer pages via templates
- Old developer CANNOT access APIs without this key
- Webhooks still work (they use signature verification)
