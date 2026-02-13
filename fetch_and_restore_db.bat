@echo off
REM Database Fetch and Restore Script for Windows
REM Usage: fetch_and_restore_db.bat <backup_filename>
REM Example: fetch_and_restore_db.bat app_backup_13-Feb-2026.sql

echo.
echo ============================================================
echo   Database Fetch and Restore Tool
echo ============================================================
echo.

REM Check if backup filename is provided
if "%1"=="" (
    echo ERROR: Backup filename not provided!
    echo.
    echo Usage:
    echo   fetch_and_restore_db.bat ^<backup_filename^>
    echo.
    echo Example:
    echo   fetch_and_restore_db.bat app_backup_13-Feb-2026.sql
    echo.
    pause
    exit /b 1
)

REM Run the Python script (try python first, then python3)
python fetch_and_restore_db.py %1 2>nul
if errorlevel 1 (
    python3 fetch_and_restore_db.py %1
)

pause
