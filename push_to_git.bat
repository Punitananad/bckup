@echo off
echo ========================================
echo Push Code to Git
echo ========================================
echo.

REM Check if there are any changes
git status --short
if errorlevel 1 (
    echo Error checking git status
    pause
    exit /b 1
)

echo.
echo ========================================
set /p commit_message="Enter commit message: "

if "%commit_message%"=="" (
    echo Error: Commit message cannot be empty!
    pause
    exit /b 1
)

echo.
echo Adding all changes...
git add .

echo.
echo Committing changes...
git commit -m "%commit_message%"

if errorlevel 1 (
    echo.
    echo No changes to commit or commit failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Select push destination:
echo 1. Main repository (origin main)
echo 2. Backup repository (mirror)
echo 3. Both
echo ========================================
set /p choice="Enter choice (1/2/3): "

if "%choice%"=="1" (
    echo.
    echo Pushing to main repository...
    git push origin main
    if errorlevel 1 (
        echo Push to main failed!
    ) else (
        echo Successfully pushed to main repository!
    )
)

if "%choice%"=="2" (
    echo.
    echo Pushing to backup repository...
    git push --mirror https://github.com/Punitananad/s2fbckup-copy.git
    if errorlevel 1 (
        echo Push to backup failed!
    ) else (
        echo Successfully pushed to backup repository!
    )
)

if "%choice%"=="3" (
    echo.
    echo Pushing to main repository...
    git push origin main
    if errorlevel 1 (
        echo Push to main failed!
    ) else (
        echo Successfully pushed to main repository!
    )
    
    echo.
    echo Pushing to backup repository...
    git push --mirror https://github.com/Punitananad/s2fbckup-copy.git
    if errorlevel 1 (
        echo Push to backup failed!
    ) else (
        echo Successfully pushed to backup repository!
    )
)

echo.
echo ========================================
echo Done!
echo ========================================
echo.
pause
