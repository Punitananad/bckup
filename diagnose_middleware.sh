#!/bin/bash
# Diagnose Why Middleware Is Not Working

echo "=== MIDDLEWARE DIAGNOSTIC TOOL ==="
echo ""

cd /var/www/scan2food/application/scan2food

echo "1. Checking if middleware file exists..."
if [ -f "theatreApp/middleware.py" ]; then
    echo "   ✓ middleware.py exists"
else
    echo "   ✗ middleware.py NOT FOUND!"
fi
echo ""

echo "2. Checking if middleware is registered in settings.py..."
if grep -q "theatreApp.middleware.APIKeyMiddleware" theatreApp/settings.py; then
    echo "   ✓ Middleware is registered in MIDDLEWARE list"
    grep -A 1 -B 1 "APIKeyMiddleware" theatreApp/settings.py
else
    echo "   ✗ Middleware NOT registered in settings.py!"
fi
echo ""

echo "3. Checking if API_KEY is in settings.py..."
if grep -q "API_KEY = os.environ.get" theatreApp/settings.py; then
    echo "   ✓ API_KEY configuration found in settings.py"
else
    echo "   ✗ API_KEY NOT configured in settings.py!"
fi
echo ""

echo "4. Checking if API_KEY is in .env file..."
if grep -q "API_KEY=" .env; then
    echo "   ✓ API_KEY found in .env"
    grep "API_KEY=" .env | sed 's/=.*/=***HIDDEN***/'
else
    echo "   ✗ API_KEY NOT in .env file!"
fi
echo ""

echo "5. Testing if Django can import middleware..."
source venv/bin/activate
python << 'EOF'
try:
    from theatreApp.middleware import APIKeyMiddleware
    print("   ✓ Middleware imports successfully")
except Exception as e:
    print(f"   ✗ Import failed: {e}")
EOF
echo ""

echo "6. Testing if Django loads API_KEY from settings..."
source venv/bin/activate
python << 'EOF'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theatreApp.settings')
django.setup()
from django.conf import settings
if hasattr(settings, 'API_KEY'):
    print(f"   ✓ API_KEY loaded: {settings.API_KEY[:10]}...")
else:
    print("   ✗ API_KEY not loaded in Django settings!")
EOF
echo ""

echo "7. Checking Python bytecode cache..."
CACHE_COUNT=$(find . -type d -name __pycache__ | wc -l)
PYC_COUNT=$(find . -type f -name "*.pyc" | wc -l)
echo "   __pycache__ directories: $CACHE_COUNT"
echo "   .pyc files: $PYC_COUNT"
if [ $CACHE_COUNT -gt 0 ] || [ $PYC_COUNT -gt 0 ]; then
    echo "   ⚠️  Cache exists - may need clearing"
else
    echo "   ✓ No cache files"
fi
echo ""

echo "8. Checking Gunicorn service configuration..."
if grep -q "EnvironmentFile=" /etc/systemd/system/gunicorn.service; then
    echo "   ✓ EnvironmentFile configured in gunicorn.service"
    grep "EnvironmentFile=" /etc/systemd/system/gunicorn.service
else
    echo "   ✗ EnvironmentFile NOT configured!"
fi
echo ""

echo "9. Checking if gunicorn service has errors..."
if grep -q "kk\[Unit\]" /etc/systemd/system/gunicorn.service; then
    echo "   ✗ FOUND 'kk' characters in service file - THIS IS THE PROBLEM!"
else
    echo "   ✓ No 'kk' characters found"
fi
echo ""

echo "10. Checking recent Gunicorn logs for middleware activity..."
echo "    Looking for [MIDDLEWARE] logs..."
MIDDLEWARE_LOGS=$(sudo journalctl -u gunicorn -n 100 | grep -c "\[MIDDLEWARE\]")
if [ $MIDDLEWARE_LOGS -gt 0 ]; then
    echo "   ✓ Found $MIDDLEWARE_LOGS middleware log entries"
    echo "   Recent middleware logs:"
    sudo journalctl -u gunicorn -n 100 | grep "\[MIDDLEWARE\]" | tail -5
else
    echo "   ✗ NO middleware logs found - middleware may not be running!"
fi
echo ""

echo "11. Checking Gunicorn service status..."
if systemctl is-active --quiet gunicorn; then
    echo "   ✓ Gunicorn is running"
else
    echo "   ✗ Gunicorn is NOT running!"
fi
echo ""

echo "12. Testing actual API endpoint..."
echo "    Testing: https://scan2food.com/theatre/api/theatre-detail"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://scan2food.com/theatre/api/theatre-detail)
echo "    Response code: $HTTP_CODE"
if [ "$HTTP_CODE" = "401" ]; then
    echo "   ✓ Middleware is WORKING (returned 401 without API key)"
elif [ "$HTTP_CODE" = "200" ]; then
    echo "   ✗ Middleware NOT working (returned 200 without API key)"
else
    echo "   ? Unexpected response code: $HTTP_CODE"
fi
echo ""

echo "=== DIAGNOSTIC SUMMARY ==="
echo ""
echo "If middleware is not working, check the items marked with ✗ above."
echo ""
echo "Common fixes:"
echo "  1. Clear Python cache: find . -type d -name __pycache__ -exec rm -rf {} +"
echo "  2. Fix gunicorn.service: Remove 'kk' characters"
echo "  3. Restart services: sudo systemctl restart gunicorn"
echo "  4. Check logs: sudo journalctl -u gunicorn -n 100"
