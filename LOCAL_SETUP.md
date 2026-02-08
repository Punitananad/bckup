# Local Development Setup - Scan2Food

## ✅ Configuration Complete

All settings have been optimized for local development on Windows.

## 🚀 Quick Start

### Option 1: Using Django runserver (Recommended)
```cmd
run_local.bat
```
Or manually:
```cmd
cd application\scan2food
python manage.py runserver
```

### Option 2: Using Daphne (For WebSocket testing)
```cmd
run_with_daphne.bat
```
Or manually:
```cmd
cd application\scan2food
daphne -b 127.0.0.1 -p 8000 theatreApp.asgi:application
```

## 📋 Prerequisites

Make sure these services are running:

1. **PostgreSQL** (Port 5432)
   - Database: `app`
   - User: `guru`
   - Password: `guru@2003`

2. **Redis** (Port 6379)
   - Required for channels/WebSockets
   - Required for caching

3. **Python Dependencies**
   ```cmd
   pip install -r requirements.txt
   ```

## 🔧 Changes Made for Local Development

### 1. Static Files
- ✅ Configured to serve from `static_files/scan2food-static/static/`
- ✅ No `collectstatic` needed
- ✅ Works with both runserver and Daphne

### 2. Security Settings
- ✅ Disabled HTTPS-only cookies (SESSION_COOKIE_SECURE = False)
- ✅ Changed SameSite to 'Lax' for localhost
- ✅ CSRF protection still active

### 3. URLs
- ✅ Static files served automatically in DEBUG mode
- ✅ Media files served from `application/scan2food/media/`

## 🌐 Access URLs

- **Main Application**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin/
- **Theatre Dashboard**: http://localhost:8000/theatre/
- **Admin Portal**: http://localhost:8000/admin-portal/

## 🐛 Troubleshooting

### Static files not loading?
1. Check if `static_files/scan2food-static/static/` exists
2. Verify DEBUG=True in settings.py
3. Clear browser cache (Ctrl+Shift+Delete)

### Database connection error?
```cmd
# Check PostgreSQL service
net start postgresql-x64-14

# Or check if it's running
psql -U guru -d app
```

### Redis connection error?
```cmd
# Check Redis service
redis-cli ping
# Should return: PONG
```

### Port 8000 already in use?
```cmd
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID)
taskkill /PID <PID> /F

# Or use different port
python manage.py runserver 8001
```

## 📝 Common Commands

```cmd
# Run migrations
cd application\scan2food
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Check for issues
python manage.py check

# Run tests
python manage.py test

# Access Django shell
python manage.py shell
```

## 🔄 When to Use Each Server

| Feature | runserver | Daphne |
|---------|-----------|--------|
| **Static files** | ✅ Auto | ✅ Configured |
| **Auto-reload** | ✅ Yes | ❌ No |
| **WebSockets** | ❌ No | ✅ Yes |
| **Speed** | ⚡ Fast | 🐢 Slower |
| **Use for** | Daily dev | Testing chat/live orders |

## 🎯 Recommendation

**Use `run_local.bat` (runserver) for 95% of development work.**

Only use Daphne when testing:
- Real-time order updates
- Chat functionality
- WebSocket connections

## 📦 Production Deployment Notes

When deploying to production, you'll need to:
1. Set `DEBUG = False`
2. Uncomment `STATIC_ROOT` in settings.py
3. Run `python manage.py collectstatic`
4. Revert security settings (SESSION_COOKIE_SECURE = True)
5. Use Nginx/WhiteNoise for static files
6. Use Daphne/Gunicorn with supervisor

---

**Everything is configured. Just run `run_local.bat` and start coding! 🚀**
