@echo off
REM PostgreSQL Local Setup Script for Windows
REM This script helps you set up PostgreSQL for local development

echo ========================================
echo PostgreSQL Local Setup for Scan2Food
echo ========================================
echo.

echo Step 1: Install PostgreSQL
echo --------------------------
echo If you haven't installed PostgreSQL yet:
echo 1. Download from: https://www.postgresql.org/download/windows/
echo 2. Install PostgreSQL (remember the password you set for 'postgres' user)
echo 3. Make sure PostgreSQL service is running
echo.
pause

echo.
echo Step 2: Create Database and User
echo ---------------------------------
echo We'll now create a local database and user for development
echo.
echo Please enter the PostgreSQL superuser password when prompted
echo.

REM Create database and user using psql
psql -U postgres -c "CREATE DATABASE scan2food_local;"
psql -U postgres -c "CREATE USER scan2food_dev WITH PASSWORD 'dev_password_123';"
psql -U postgres -c "ALTER ROLE scan2food_dev SET client_encoding TO 'utf8';"
psql -U postgres -c "ALTER ROLE scan2food_dev SET default_transaction_isolation TO 'read committed';"
psql -U postgres -c "ALTER ROLE scan2food_dev SET timezone TO 'Asia/Kolkata';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE scan2food_local TO scan2food_dev;"
psql -U postgres -d scan2food_local -c "GRANT ALL ON SCHEMA public TO scan2food_dev;"

echo.
echo Step 3: Restore Database Backup
echo --------------------------------
echo Restoring data from dbbckup.sql...
echo.

REM Restore the backup
psql -U scan2food_dev -d scan2food_local -f dbbckup.sql

echo.
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
echo These credentials are already configured in your .env file
echo.
echo Next steps:
echo 1. Install psycopg2: pip install psycopg2-binary
echo 2. Run migrations: python application/scan2food/manage.py migrate
echo 3. Start your server: run_local.bat
echo.
pause
