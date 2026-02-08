# ✅ Local Development Checklist

## Before Starting the Server

### 1. Services Running
- [ ] PostgreSQL is running (Port 5432)
  ```cmd
  net start postgresql-x64-14
  ```
- [ ] Redis is running (Port 6379)
  ```cmd
  redis-server
  # Or check: redis-cli ping
  ```

### 2. Database Setup
- [ ] Database exists: `app`
- [ ] User credentials match:
  - User: `guru`
  - Password: `guru@2003`
- [ ] Migrations applied:
  ```cmd
  cd application\scan2food
  python manage.py migrate
  ```

### 3. Python Dependencies
- [ ] All packages installed:
  ```cmd
  pip install -r requirements.txt
  ```

### 4. Static Files
- [ ] Static files directory exists:
  ```cmd
  dir static_files\scan2food-static\static\manifest.json
  ```
- [ ] Run test script:
  ```cmd
  test_static.bat
  ```

## Starting Development

### Option A: Django runserver (Recommended)
```cmd
run_local.bat
```
**Use this for:**
- Regular development
- Testing views and templates
- Database operations
- Most day-to-day work

### Option B: Daphne ASGI
```cmd
run_with_daphne.bat
```
**Use this only for:**
- Testing WebSocket connections
- Testing real-time order updates
- Testing chat functionality

## Verification Steps

After starting the server:

1. [ ] Server starts without errors
2. [ ] Visit http://localhost:8000
3. [ ] Check browser console (F12) - no 404 errors for static files
4. [ ] Static files loading:
   - [ ] CSS styles applied
   - [ ] Images visible
   - [ ] JavaScript working

## Common Issues & Solutions

### ❌ Static files 404
**Solution:**
1. Verify `static_files/scan2food-static/static/` exists
2. Clear browser cache (Ctrl+Shift+Delete)
3. Hard refresh (Ctrl+F5)
4. Check DEBUG=True in settings.py

### ❌ Database connection refused
**Solution:**
```cmd
# Check if PostgreSQL is running
net start postgresql-x64-14

# Test connection
psql -U guru -d app
```

### ❌ Redis connection error
**Solution:**
```cmd
# Start Redis
redis-server

# Or check if running
redis-cli ping
# Should return: PONG
```

### ❌ Port 8000 already in use
**Solution:**
```cmd
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace <PID> with actual number)
taskkill /PID <PID> /F

# Or use different port
python manage.py runserver 8001
```

### ❌ Module not found errors
**Solution:**
```cmd
pip install -r requirements.txt
```

### ❌ CSRF verification failed
**Solution:**
- Already fixed! Cookie settings changed to work with localhost
- If still issues, clear browser cookies

## Development Workflow

1. **Start server**: `run_local.bat`
2. **Make code changes**: Files auto-reload
3. **Test in browser**: http://localhost:8000
4. **Check logs**: Terminal shows requests and errors
5. **Stop server**: Press Ctrl+C

## Quick Commands Reference

```cmd
# Navigate to project
cd application\scan2food

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell

# Check for issues
python manage.py check

# Run tests
python manage.py test

# Start server
python manage.py runserver

# Start with Daphne
daphne -b 127.0.0.1 -p 8000 theatreApp.asgi:application
```

## Files Modified for Local Development

✅ `application/scan2food/theatreApp/settings.py`
- Static files configuration
- Cookie security settings

✅ `application/scan2food/theatreApp/urls.py`
- Static file serving in DEBUG mode

## Production Deployment Notes

When deploying to production, remember to:
1. Set `DEBUG = False`
2. Uncomment `STATIC_ROOT` in settings.py
3. Run `python manage.py collectstatic`
4. Revert cookie settings:
   - `SESSION_COOKIE_SECURE = True`
   - `CSRF_COOKIE_SECURE = True`
   - `SESSION_COOKIE_SAMESITE = 'None'`
5. Configure Nginx/WhiteNoise for static files

---

**Everything is ready! Start with: `run_local.bat` 🚀**
