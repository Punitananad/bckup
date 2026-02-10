# 🚀 Deploy Changes to Production Server

## Changes Made That Need Deployment:

1. ✅ Fixed permission checks in `adminPortal/views.py` (28 fixes)
2. ✅ Fixed permission checks in `theatre/views.py` (31 fixes)
3. ✅ Fixed `adminPortal/decorator.py` - Allow superusers
4. ✅ Fixed `theatre/decorator.py` - Handle missing theatre.detail
5. ✅ Fixed `theatre/admin.py` - Handle theatres without users
6. ✅ Added new IP to ALLOWED_HOSTS

## Deployment Steps:

### Step 1: SSH to Production Server
```bash
ssh root@165.22.219.111
```

### Step 2: Pull Latest Code
```bash
cd /var/www/scan2food
git pull origin main
```

### Step 3: Activate Virtual Environment
```bash
source application/scan2food/venv/bin/activate
cd application/scan2food
```

### Step 4: Install Any New Dependencies (if needed)
```bash
pip install -r requirements.txt
```

### Step 5: Run Migrations (if any)
```bash
python manage.py migrate
```

### Step 6: Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Step 7: Restart Services
```bash
sudo systemctl restart scan2food
sudo systemctl restart nginx
```

### Step 8: Check Status
```bash
sudo systemctl status scan2food
```

### Step 9: Check Logs (if there are errors)
```bash
# Daphne logs
sudo journalctl -u scan2food -n 50

# Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

---

## Quick One-Line Deployment:

```bash
ssh root@165.22.219.111 "cd /var/www/scan2food && git pull origin main && source application/scan2food/venv/bin/activate && cd application/scan2food && python manage.py migrate && python manage.py collectstatic --noinput && sudo systemctl restart scan2food && sudo systemctl status scan2food"
```

---

## After Deployment:

1. Test the URL that was giving 500 error
2. Check if you can add food items
3. Verify admin portal works
4. Test theatre dashboard

---

## If Still Getting 500 Error:

Check the logs:
```bash
ssh root@165.22.219.111
sudo journalctl -u scan2food -n 100
```

This will show you the exact error happening on production.

---

**Note:** All the fixes we made are already pushed to GitHub, so you just need to pull and restart the service!
