@echo off
echo ========================================
echo Starting Scan2Food Local Development
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "application\scan2food\manage.py" (
    echo ERROR: Please run this script from the project root directory!
    echo Current directory: %CD%
    echo Expected: Should contain application\scan2food\manage.py
    echo.
    pause
    exit /b 1
)

cd application\scan2food

REM Set API_KEY environment variable
set API_KEY=ecdcfdf9ea6840e4ef23f8e1dd3991725ad08a624632f854c043fd3236d49b28
set DJANGO_ENV=development
echo API_KEY loaded: %API_KEY:~0,10%...
echo Environment: %DJANGO_ENV%
echo.

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

cd ..\..
pause
