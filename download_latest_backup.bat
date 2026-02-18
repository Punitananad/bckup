@echo off
REM Download Latest Database Backup from Production Server
REM This script downloads the most recent backup to your Downloads folder

echo ==========================================
echo DOWNLOAD LATEST DATABASE BACKUP
echo ==========================================
echo.

REM Set variables
set SERVER=root@165.22.219.111
set BACKUP_DIR=/var/www/scan2food/application/scan2food/backupScript/backups
set LOCAL_DIR=C:\Users\punit\Downloads
set TIMESTAMP=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

echo Step 1: Connecting to server...
echo Server: %SERVER%
echo.

REM Create a temporary script to find and download the latest backup
echo Finding latest backup file...
echo.

REM Use SCP to download the latest backup
REM First, get the latest backup filename
ssh %SERVER% "ls -t %BACKUP_DIR%/*.sql | head -n 1" > temp_latest.txt
set /p LATEST_BACKUP=<temp_latest.txt
del temp_latest.txt

if "%LATEST_BACKUP%"=="" (
    echo ERROR: No backup files found on server!
    echo Please check if backups exist at: %BACKUP_DIR%
    pause
    exit /b 1
)

echo Latest backup found: %LATEST_BACKUP%
echo.

REM Extract just the filename
for %%F in (%LATEST_BACKUP%) do set BACKUP_FILENAME=%%~nxF

echo Step 2: Downloading backup...
echo From: %LATEST_BACKUP%
echo To: %LOCAL_DIR%\%BACKUP_FILENAME%
echo.

REM Download using SCP
scp %SERVER%:%LATEST_BACKUP% "%LOCAL_DIR%\%BACKUP_FILENAME%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==========================================
    echo SUCCESS!
    echo ==========================================
    echo.
    echo Backup downloaded successfully!
    echo Location: %LOCAL_DIR%\%BACKUP_FILENAME%
    echo.
    echo File size:
    dir "%LOCAL_DIR%\%BACKUP_FILENAME%" | find "%BACKUP_FILENAME%"
    echo.
) else (
    echo.
    echo ==========================================
    echo ERROR!
    echo ==========================================
    echo.
    echo Failed to download backup.
    echo Please check:
    echo 1. SSH connection is working
    echo 2. Backup files exist on server
    echo 3. You have write permissions to Downloads folder
    echo.
)

pause
