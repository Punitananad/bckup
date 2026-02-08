@echo off
echo ========================================
echo Starting Scan2Food Local Development
echo ========================================
echo.

cd application\scan2food

echo Checking configuration...
python manage.py check --database default 2>nul
if errorlevel 1 (
    echo.
    echo WARNING: Some configuration issues detected.
    echo This is normal for local development.
    echo.
)

echo Starting Django development server...
echo.
echo Access your application at: http://localhost:8000
echo Press CTRL+C to stop the server
echo.

python manage.py runserver

pause
