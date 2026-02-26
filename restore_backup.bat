@echo off
REM Script to restore database backup to local PostgreSQL

echo ========================================
echo Restore Database Backup
echo ========================================
echo.
echo This will restore dbbckup.sql to your local database
echo WARNING: This will overwrite existing data!
echo.
pause

echo.
echo Dropping existing database (if exists)...
psql -U postgres -c "DROP DATABASE IF EXISTS scan2food_local;"

echo Creating fresh database...
psql -U postgres -c "CREATE DATABASE scan2food_local;"

echo Granting permissions...
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE scan2food_local TO scan2food_dev;"
psql -U postgres -d scan2food_local -c "GRANT ALL ON SCHEMA public TO scan2food_dev;"

echo.
echo Restoring backup...
psql -U scan2food_dev -d scan2food_local -f dbbckup.sql

echo.
echo ========================================
echo Restore Complete!
echo ========================================
echo.
pause
