@echo off
REM Quick check if PostgreSQL is installed and accessible

echo Checking PostgreSQL installation...
echo.

REM Check if psql command is available
where psql >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ PostgreSQL is installed and in PATH
    echo.
    psql --version
    echo.
    echo PostgreSQL service status:
    sc query postgresql-x64-16 2>nul | find "STATE"
    if %ERRORLEVEL% NEQ 0 (
        sc query postgresql-x64-15 2>nul | find "STATE"
        if %ERRORLEVEL% NEQ 0 (
            sc query postgresql-x64-14 2>nul | find "STATE"
        )
    )
    echo.
    echo ✅ You're ready to run: setup_postgres_local.bat
) else (
    echo ❌ PostgreSQL is not installed or not in PATH
    echo.
    echo Please:
    echo 1. Install PostgreSQL from: https://www.postgresql.org/download/windows/
    echo 2. Or add PostgreSQL to PATH: C:\Program Files\PostgreSQL\16\bin
    echo.
)

echo.
pause
