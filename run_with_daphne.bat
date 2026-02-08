@echo off
echo ========================================
echo Starting Scan2Food with Daphne (ASGI)
echo ========================================
echo.

cd application\scan2food

echo Checking services...
python manage.py check
if errorlevel 1 (
    echo.
    echo ERROR: Configuration issue detected!
    pause
    exit /b 1
)

echo.
echo Starting Daphne ASGI server...
echo.
echo Access your application at: http://localhost:8000
echo WebSockets enabled for real-time features
echo Press CTRL+C to stop the server
echo.

daphne -b 127.0.0.1 -p 8000 theatreApp.asgi:application

pause
