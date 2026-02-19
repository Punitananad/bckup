@echo off
echo ========================================
echo Upload Theatre Logos to Server
echo ========================================
echo.

set LOCAL_PATH=application\scan2food\media\theatre_logo
set SERVER_USER=root
set SERVER_IP=165.22.219.111
set SERVER_PATH=/var/www/scan2food/application/scan2food/media/theatre_logo/

echo Checking local theatre_logo folder...
if not exist "%LOCAL_PATH%" (
    echo Error: Local theatre_logo folder not found!
    echo Expected path: %LOCAL_PATH%
    pause
    exit /b 1
)

echo.
echo Local images found:
dir /b "%LOCAL_PATH%"

echo.
echo Uploading images to server...
echo.

scp -r %LOCAL_PATH%\* %SERVER_USER%@%SERVER_IP%:%SERVER_PATH%

if errorlevel 1 (
    echo.
    echo Upload failed! Make sure:
    echo 1. You have SSH access to the server
    echo 2. SCP is installed (comes with Git Bash or PuTTY)
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Successfully uploaded all theatre logos!
echo ========================================
echo.
pause
