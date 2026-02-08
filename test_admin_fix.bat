@echo off
cd application\scan2food
echo Testing admin configuration...
python manage.py check 2>&1 | findstr /C:"admin.E108"
if errorlevel 1 (
    echo [OK] Admin errors fixed!
) else (
    echo [ERROR] Admin errors still present
)
pause
