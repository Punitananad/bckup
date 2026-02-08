@echo off
echo ========================================
echo Setting Up SQLite Database
echo ========================================
echo.

cd application\scan2food

echo Step 1: Running migrations...
python manage.py migrate

if errorlevel 1 (
    echo.
    echo [ERROR] Migration failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! Database created.
echo ========================================
echo.
echo Next steps:
echo.
echo 1. Create a superuser (admin account):
echo    python manage.py createsuperuser
echo.
echo 2. Start the server:
echo    run_local.bat
echo.
echo Or run both now? (y/n)
set /p runnow="Create superuser now? (y/n): "

if /i "%runnow%"=="y" (
    echo.
    echo Creating superuser...
    python manage.py createsuperuser
)

echo.
echo ========================================
echo Setup complete! You can now run:
echo   run_local.bat
echo ========================================
echo.
pause
