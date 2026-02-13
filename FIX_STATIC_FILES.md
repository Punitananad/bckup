# Fix Static Files Loading Issue

## Problem
Browser console shows `net::ERR_UNKNOWN_URL_SCHEME` errors when trying to load static files (CSS, JS, images).

## Solution Steps

### 1. Verify Django Development Server is Running
Make sure you're running the development server:
```bash
cd application\scan2food
python manage.py runserver
```

### 2. Check Static Files Configuration
Your `settings.py` already has the correct configuration:
```python
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR.parent.parent, 'static_files', 'scan2food-static', 'static'),
]
```

### 3. Verify Static Files Directory Exists
Check that this path exists:
```
static_files/scan2food-static/static/
```

### 4. Clear Browser Cache
- Press `Ctrl + Shift + Delete` in your browser
- Clear cached images and files
- Or use `Ctrl + F5` to hard refresh the page

### 5. Check for HTTPS/HTTP Issues
If you're accessing via `http://localhost:8000`, make sure:
- No browser extensions are forcing HTTPS
- No redirect rules in your code

### 6. Test Static Files Directly
Try accessing a static file directly in your browser:
```
http://localhost:8000/static/assets/css/style.css
```

If this returns a 404, the static files aren't being served.

### 7. Run Django's collectstatic (if needed)
```bash
python manage.py collectstatic --noinput
```

### 8. Check for Template Syntax Errors
Make sure all `{% load static %}` tags are at the top of templates that use static files.

## Common Causes

1. **Server not running** - Most common issue
2. **Wrong URL** - Accessing via IP instead of localhost
3. **Browser cache** - Old cached resources causing issues
4. **Static files path incorrect** - Directory doesn't exist
5. **Template syntax error** - Missing `{% load static %}`

## Quick Test
1. Stop the server (Ctrl+C)
2. Run: `run_local.bat`
3. Open: `http://localhost:8000/theatre/live-orders/`
4. Check browser console

## If Still Not Working
Check the Django development server console output for any errors when accessing static files.
