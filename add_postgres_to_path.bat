@echo off
REM Add PostgreSQL to Windows PATH permanently

echo ========================================
echo Add PostgreSQL to System PATH
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
    echo Please manually add PostgreSQL to your PATH:
    echo 1. Find your PostgreSQL installation folder
    echo 2. Search for "Environment Variables" in Windows
    echo 3. Edit "Path" in System Variables
    echo 4. Add the bin folder path
    echo.
    pause
    exit /b 1
)

echo Found PostgreSQL at: %PGPATH%
echo.
echo To add this to your PATH permanently:
echo.
echo 1. Press Windows key and search for "Environment Variables"
echo 2. Click "Edit the system environment variables"
echo 3. Click "Environment Variables" button
echo 4. Under "System variables", find and select "Path"
echo 5. Click "Edit"
echo 6. Click "New"
echo 7. Paste this path: %PGPATH%
echo 8. Click "OK" on all windows
echo 9. Restart Command Prompt
echo.
echo The path to add is:
echo %PGPATH%
echo.
echo Would you like to copy this path to clipboard? (Y/N)
set /p choice=

if /i "%choice%"=="Y" (
    echo %PGPATH% | clip
    echo ✅ Path copied to clipboard!
    echo Now follow the steps above to add it to your PATH
)

echo.
pause
