@echo off
REM First-time setup script for Scan2Food local development
REM This script will guide you through the entire setup process

echo ============================================================
echo Scan2Food - First Time Setup
echo ============================================================
echo.
echo This script will help you set up your local development environment
echo with PostgreSQL database.
echo.
pause

echo.
echo ============================================================
echo Step 1: Checking PostgreSQL Installation
echo ============================================================
echo.

where psql >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ PostgreSQL is not installed or not in PATH
    echo.
    echo Please install PostgreSQL first:
    echo 1. Download from: https://www.postgresql.org/download/windows/
    echo 2. Install PostgreSQL (remember the password for 'postgres' user)
    echo 3. Make sure to add PostgreSQL to PATH during installation
    echo.
    echo After installation, run this script again.
    echo.
    pause
    exit /b 1
)

echo ✅ PostgreSQL is installed
psql --version
echo.
pause

echo.
echo ============================================================
echo Step 2: Installing Python Dependencies
echo ============================================================
echo.

cd application\scan2food
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to install dependencies
    echo Please check your Python installation and try again
    pause
    exit /b 1
)
cd ..\..

echo ✅ Dependencies installed
echo.
pause

echo.
echo ============================================================
echo Step 3: Setting Up PostgreSQL Database
echo ============================================================
echo.
echo This will create a local database and restore your backup
echo You'll be prompted for the PostgreSQL 'postgres' user password
echo.
pause

call setup_postgres_local.bat

echo.
echo ============================================================
echo Step 4: Verifying Database Setup
echo ============================================================
echo.

python verify_postgres_setup.py
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Database verification failed
    echo Please check the error messages above
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Step 5: Running Django Migrations
echo ============================================================
echo.

cd application\scan2food
python manage.py migrate
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Migrations had some issues, but this might be okay
    echo if the backup was already restored
)
cd ..\..

echo.
echo ============================================================
echo ✅ Setup Complete!
echo ============================================================
echo.
echo Your local development environment is ready!
echo.
echo Database Configuration:
echo   Database: scan2food_local
echo   User: scan2food_dev
echo   Password: dev_password_123
echo   Host: localhost
echo   Port: 5432
echo.
echo To start your development server, run:
echo   run_local.bat
echo.
echo To verify setup anytime, run:
echo   python verify_postgres_setup.py
echo.
echo Documentation:
echo   - Quick Start: QUICK_START_POSTGRES.md
echo   - Detailed Guide: POSTGRES_SETUP_GUIDE.md
echo   - Migration Info: README_POSTGRES_MIGRATION.md
echo.
pause
