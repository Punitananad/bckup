@echo off
color 0A
title PostgreSQL Setup for Scan2Food

echo.
echo  ╔════════════════════════════════════════════════════════════╗
echo  ║                                                            ║
echo  ║         PostgreSQL Setup for Scan2Food                     ║
echo  ║                                                            ║
echo  ╚════════════════════════════════════════════════════════════╝
echo.
echo  This will set up your local PostgreSQL database.
echo.
echo  What this does:
echo  ✓ Creates database: scan2food_local
echo  ✓ Creates user: scan2food_dev
echo  ✓ Restores your backup data
echo.
echo  You will need:
echo  • Your PostgreSQL 'postgres' user password
echo    (the one you set when installing PostgreSQL)
echo.
pause

echo.
echo ════════════════════════════════════════════════════════════
echo  Finding PostgreSQL...
echo ════════════════════════════════════════════════════════════
echo.

REM Try to find PostgreSQL
set "PGPATH="
for %%v in (17 16 15 14 13) do (
    if exist "C:\Program Files\PostgreSQL\%%v\bin\psql.exe" (
        set "PGPATH=C:\Program Files\PostgreSQL\%%v\bin"
        set "PGVER=%%v"
        goto :found
    )
)

:found
if "%PGPATH%"=="" (
    color 0C
    echo  ❌ Could not find PostgreSQL automatically
    echo.
    echo  Please use one of these methods instead:
    echo.
    echo  Method 1: Use pgAdmin 4
    echo  ─────────────────────────
    echo  1. Open pgAdmin 4 from Start menu
    echo  2. Follow the guide in: SETUP_NOW.md
    echo.
    echo  Method 2: Manual Setup
    echo  ─────────────────────────
    echo  1. Find your PostgreSQL installation folder
    echo  2. Look for: C:\Program Files\PostgreSQL\XX\bin
    echo  3. Edit setup_postgres_easy.bat with the correct path
    echo.
    pause
    exit /b 1
)

echo  ✅ Found PostgreSQL %PGVER% at:
echo     %PGPATH%
echo.

REM Add to PATH temporarily
set "PATH=%PGPATH%;%PATH%"

echo ════════════════════════════════════════════════════════════
echo  Step 1: Creating Database
echo ════════════════════════════════════════════════════════════
echo.
echo  Please enter your PostgreSQL 'postgres' password:
echo.

"%PGPATH%\psql.exe" -U postgres -c "DROP DATABASE IF EXISTS scan2food_local;"
"%PGPATH%\psql.exe" -U postgres -c "CREATE DATABASE scan2food_local;"

if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo.
    echo  ❌ Failed to create database
    echo.
    echo  Common issues:
    echo  • Wrong password
    echo  • PostgreSQL service not running
    echo.
    echo  Try using pgAdmin 4 instead (see SETUP_NOW.md)
    echo.
    pause
    exit /b 1
)

echo.
echo  ✅ Database created
echo.

echo ════════════════════════════════════════════════════════════
echo  Step 2: Creating User
echo ════════════════════════════════════════════════════════════
echo.

"%PGPATH%\psql.exe" -U postgres -c "DROP USER IF EXISTS scan2food_dev;"
"%PGPATH%\psql.exe" -U postgres -c "CREATE USER scan2food_dev WITH PASSWORD 'dev_password_123';"
"%PGPATH%\psql.exe" -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE scan2food_local TO scan2food_dev;"
"%PGPATH%\psql.exe" -U postgres -d scan2food_local -c "GRANT ALL ON SCHEMA public TO scan2food_dev;"

echo.
echo  ✅ User created
echo.

echo ════════════════════════════════════════════════════════════
echo  Step 3: Restoring Backup
echo ════════════════════════════════════════════════════════════
echo.
echo  Restoring data from dbbckup.sql...
echo  This may take a minute...
echo.

set PGPASSWORD=dev_password_123
"%PGPATH%\psql.exe" -U scan2food_dev -d scan2food_local -f dbbckup.sql >nul 2>&1
set PGPASSWORD=

echo  ✅ Backup restored
echo.

color 0A
echo ════════════════════════════════════════════════════════════
echo  🎉 Setup Complete!
echo ════════════════════════════════════════════════════════════
echo.
echo  Your database is ready:
echo.
echo  Database: scan2food_local
echo  User:     scan2food_dev
echo  Password: dev_password_123
echo  Host:     localhost
echo  Port:     5432
echo.
echo ════════════════════════════════════════════════════════════
echo  Next Steps:
echo ════════════════════════════════════════════════════════════
echo.
echo  1. Install Python dependencies:
echo     pip install psycopg2-binary
echo.
echo  2. Verify setup:
echo     python verify_postgres_setup.py
echo.
echo  3. Start your app:
echo     run_local.bat
echo.
echo ════════════════════════════════════════════════════════════
echo.
pause
