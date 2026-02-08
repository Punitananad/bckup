@echo off
echo ========================================
echo DATABASE SETUP WIZARD
echo ========================================
echo.
echo This will help you fix the database connection error.
echo.
echo Current Error:
echo   password authentication failed for user "guru"
echo.
echo ========================================
echo CHOOSE YOUR SOLUTION:
echo ========================================
echo.
echo 1. Use SQLite (Easiest - No PostgreSQL needed)
echo 2. Use PostgreSQL with 'postgres' user
echo 3. Create 'guru' user in PostgreSQL
echo 4. Show me how to check my PostgreSQL credentials
echo 5. Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto sqlite
if "%choice%"=="2" goto postgres_user
if "%choice%"=="3" goto create_guru
if "%choice%"=="4" goto check_creds
if "%choice%"=="5" goto end

:sqlite
echo.
echo ========================================
echo OPTION 1: Using SQLite
echo ========================================
echo.
echo This will:
echo 1. Update settings.py to use SQLite
echo 2. Create a local database file
echo 3. Run migrations
echo.
echo Pros: No PostgreSQL needed, simple setup
echo Cons: Different from production (but fine for development)
echo.
set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" goto end

echo.
echo Creating backup of settings.py...
copy application\scan2food\theatreApp\settings.py application\scan2food\theatreApp\settings.py.backup

echo.
echo To use SQLite, edit this file:
echo   application\scan2food\theatreApp\settings.py
echo.
echo Find the DATABASES section and replace with:
echo.
echo DATABASES = {
echo     'default': {
echo         'ENGINE': 'django.db.backends.sqlite3',
echo         'NAME': BASE_DIR / 'db.sqlite3',
echo     }
echo }
echo.
echo Then run:
echo   cd application\scan2food
echo   python manage.py migrate
echo   python manage.py createsuperuser
echo   python manage.py runserver
echo.
pause
goto end

:postgres_user
echo.
echo ========================================
echo OPTION 2: Using 'postgres' User
echo ========================================
echo.
echo Testing connection with 'postgres' user...
psql -U postgres -c "SELECT version();" 2>nul
if errorlevel 1 (
    echo [FAILED] Cannot connect with 'postgres' user
    echo.
    echo Please enter your PostgreSQL password when prompted:
    psql -U postgres -c "SELECT version();"
    if errorlevel 1 (
        echo.
        echo Still cannot connect. Please check:
        echo 1. PostgreSQL is running: net start postgresql-x64-14
        echo 2. You know the postgres password
        echo.
        pause
        goto end
    )
)

echo.
echo [SUCCESS] Connected!
echo.
set /p dbname="Enter database name to create (default: scan2food_local): "
if "%dbname%"=="" set dbname=scan2food_local

echo.
echo Creating database '%dbname%'...
psql -U postgres -c "CREATE DATABASE %dbname%;" 2>nul
if errorlevel 1 (
    echo Database might already exist, continuing...
)

echo.
echo Now update your settings.py:
echo   File: application\scan2food\theatreApp\settings.py
echo.
echo Change DATABASES to:
echo.
echo DATABASES = {
echo     'default': {
echo         'ENGINE': 'django.db.backends.postgresql',
echo         'NAME': '%dbname%',
echo         'USER': 'postgres',
echo         'PASSWORD': 'your_postgres_password',
echo         'HOST': 'localhost',
echo         'PORT': '5432',
echo     }
echo }
echo.
pause
goto end

:create_guru
echo.
echo ========================================
echo OPTION 3: Creating 'guru' User
echo ========================================
echo.
echo This will create the user that matches your settings.py
echo.
echo Opening PostgreSQL... (enter postgres password when prompted)
echo.
echo Run these commands:
echo   CREATE USER guru WITH PASSWORD 'guru@2003';
echo   CREATE DATABASE app OWNER guru;
echo   GRANT ALL PRIVILEGES ON DATABASE app TO guru;
echo   \q
echo.
pause
psql -U postgres
echo.
echo If successful, try running: run_local.bat
echo.
pause
goto end

:check_creds
echo.
echo ========================================
echo OPTION 4: Check PostgreSQL Credentials
echo ========================================
echo.
echo Method 1: List all PostgreSQL users
echo -------------------------------------
psql -U postgres -c "\du" 2>nul
if errorlevel 1 (
    echo Cannot connect. Try entering password:
    psql -U postgres -c "\du"
)

echo.
echo Method 2: Check PostgreSQL service
echo -------------------------------------
sc query | findstr /i postgres

echo.
echo Method 3: Try connecting
echo -------------------------------------
echo Testing with 'postgres' user...
psql -U postgres -l 2>nul

echo.
echo Your settings.py currently has:
echo   User: guru
echo   Password: guru@2003
echo   Database: app
echo.
echo Update settings.py with your actual credentials.
echo.
pause
goto end

:end
echo.
echo ========================================
echo For more details, read:
echo   QUICK_FIX_DATABASE.md
echo ========================================
echo.
pause
