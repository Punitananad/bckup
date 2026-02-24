@echo off
echo ============================================================
echo Starting Scan2Food Local Development Server
echo ============================================================
echo.

cd application\scan2food

echo Starting Django development server...
echo Server will be available at: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.

python manage.py runserver

pause
