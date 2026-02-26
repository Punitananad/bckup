@echo off
REM Easy PostgreSQL Setup - Finds PostgreSQL automatically

echo ========================================
echo PostgreSQL Setup for Scan2Food
echo ========================================
echo.

REM Try to find PostgreSQL installation
set "PGPATH="
for %%v in (17 16 15 14 13) do (
    if exist "C:\Program Files\PostgreSQL\%%v\bin\psql.exe" (
        set "PGPATH=C:\Program Files\PostgreSQL\%%v\bin"
        goto :found
    )
)

:found
if "%PGPATH%"=="" (
    echo ❌ Could not find PostgreSQL installation
    echo.
    echo Please find your PostgreSQL installation folder and run:
    echo "C:\Program Files\PostgreSQL\XX\bin\psql.exe" --version
    echo.
    echo Then update this script with the correct path.
    pause
    exit /b 1
)

echo ✅ Found PostgreSQL at: %PGPATH%
echo.

REM Add to PATH temporarily for this session
set "PATH=%PGPATH%;%PATH%"

echo Step 1: Creating Database and User
echo -----------------------------------
echo Please enter your PostgreSQL 'postgres' user password when prompted
echo.

REM Create database and user
"%PGPATH%\psql.exe" -U postgres -c "DROP DATABASE IF EXISTS scan2food_local;"
"%PGPATH%\psql.exe" -U postgres -c "CREATE DATABASE scan2food_local;"
"%PGPATH%\psql.exe" -U postgres -c "DROP USER IF EXISTS scan2food_dev;"
"%PGPATH%\psql.exe" -U postgres -c "CREATE USER scan2food_dev WITH PASSWORD 'dev_password_123';"
"%PGPATH%\psql.exe" -U postgres -c "ALTER ROLE scan2food_dev SET client_encoding TO 'utf8';"
"%PGPATH%\psql.exe" -U postgres -c "ALTER ROLE scan2food_dev SET default_transaction_isolation TO 'read committed';"
"%PGPATH%\psql.exe" -U postgres -c "ALTER ROLE scan2food_dev SET timezone TO 'Asia/Kolkata';"
"%PGPATH%\psql.exe" -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE scan2food_local TO scan2food_dev;"
"%PGPATH%\psql.exe" -U postgres -d scan2food_local -c "GRANT ALL ON SCHEMA public TO scan2food_dev;"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Failed to create database
    echo Please check your PostgreSQL password and try again
    pause
    exit /b 1
)

echo.
echo ✅ Database and user created successfully
echo.

echo Step 2: Restoring Backup
echo ------------------------
echo Restoring data from dbbckup.sql...
echo Password for scan2food_dev: dev_password_123
echo.

REM Set password environment variable to avoid prompt
set PGPASSWORD=dev_password_123
"%PGPATH%\psql.exe" -U scan2food_dev -d scan2food_local -f dbbckup.sql
set PGPASSWORD=

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ⚠️  Backup restore had some errors
    echo This might be okay if the database structure was already created
    echo.
) else (
    echo.
    echo ✅ Backup restored successfully
    echo.
)

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Your local PostgreSQL database is ready:
echo   Database: scan2food_local
echo   User: scan2food_dev
echo   Password: dev_password_123
echo   Host: localhost
echo   Port: 5432
echo.
echo PostgreSQL location: %PGPATH%
echo.
echo Next steps:
echo 1. Install Python dependencies: pip install psycopg2-binary
echo 2. Run migrations: cd application\scan2food ^& python manage.py migrate
echo 3. Start server: run_local.bat
echo.
echo To add PostgreSQL to your PATH permanently:
echo 1. Search for "Environment Variables" in Windows
echo 2. Edit "Path" in System Variables
echo 3. Add: %PGPATH%
echo.
pause
