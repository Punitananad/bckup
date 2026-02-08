@echo off
echo ========================================
echo Testing Static Files Configuration
echo ========================================
echo.

echo Checking if static files directory exists...
if exist "static_files\scan2food-static\static\manifest.json" (
    echo [OK] manifest.json found
) else (
    echo [ERROR] manifest.json NOT found
    echo Expected location: static_files\scan2food-static\static\manifest.json
    pause
    exit /b 1
)

if exist "static_files\scan2food-static\static\assets" (
    echo [OK] assets folder found
) else (
    echo [ERROR] assets folder NOT found
)

if exist "static_files\scan2food-static\static\sound" (
    echo [OK] sound folder found
) else (
    echo [ERROR] sound folder NOT found
)

echo.
echo Testing Django configuration...
python -c "import sys; sys.path.insert(0, 'application/scan2food'); import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theatreApp.settings'); import django; django.setup(); from django.conf import settings; print('[OK] STATIC_URL:', settings.STATIC_URL); print('[OK] DEBUG:', settings.DEBUG); print('[OK] Static path:', settings.STATICFILES_DIRS[0])"

if errorlevel 1 (
    echo [ERROR] Django configuration issue
    pause
    exit /b 1
)

echo.
echo ========================================
echo All checks passed! Static files ready.
echo ========================================
echo.
echo You can now run: run_local.bat
echo.
pause
