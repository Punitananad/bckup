@echo off
echo ========================================
echo PostgreSQL Database Setup Helper
echo ========================================
echo.
echo Current settings.py configuration:
echo   Database: app
echo   User: guru
echo   Password: guru@2003
echo   Host: localhost
echo   Port: 5432
echo.
echo ========================================
echo Testing PostgreSQL Connection
echo ========================================
echo.

echo Option 1: Test with current credentials
echo -----------------------------------------
psql -U guru -d app -c "SELECT version();" 2>nul
if errorlevel 1 (
    echo [FAILED] Cannot connect with user 'guru'
    echo.
    echo Possible solutions:
    echo.
    echo 1. Check if PostgreSQL is running:
    echo    net start postgresql-x64-14
    echo.
    echo 2. Check your PostgreSQL username:
    echo    psql -U postgres -c "\du"
    echo.
    echo 3. Create the user and database:
    echo    psql -U postgres
    echo    CREATE USER guru WITH PASSWORD 'guru@2003';
    echo    CREATE DATABASE app OWNER guru;
    echo    GRANT ALL PRIVILEGES ON DATABASE app TO guru;
    echo    \q
    echo.
    echo 4. Or update settings.py with your actual credentials
    echo.
) else (
    echo [SUCCESS] Connected to PostgreSQL!
    echo Database is ready.
)

echo.
echo ========================================
echo Quick Fix Options
echo ========================================
echo.
echo A. Use default 'postgres' user (easiest)
echo B. Create 'guru' user with correct password
echo C. Find your existing PostgreSQL credentials
echo.
pause
