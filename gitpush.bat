@echo off
echo ============================================================
echo Git Push to Repository
echo ============================================================
echo.

REM Check if there are any changes
git status

echo.
set /p commit_msg="Enter commit message: "

if "%commit_msg%"=="" (
    echo Error: Commit message cannot be empty
    pause
    exit /b 1
)

echo.
echo Adding all changes...
git add .

echo.
echo Committing changes...
git commit -m "%commit_msg%"

echo.
echo Pushing to origin main...
git push origin main

echo.
echo ============================================================
echo Push completed!
echo ============================================================
echo.
pause
