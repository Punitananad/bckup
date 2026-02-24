@echo off
echo ============================================================
echo Git Push to Repository (Force Push - No Pull)
echo ============================================================
echo.

echo Adding all changes...
git add .

echo.
echo Committing changes...
git commit -m "Update: Fix countdown logic for authenticated users"

echo.
echo Force pushing to origin main...
git push origin main --force

echo.
echo ============================================================
echo Push completed!
echo ============================================================
echo.
pause
