# PostgreSQL Local Setup Guide

This guide will help you migrate from SQLite to PostgreSQL for local development.

## Prerequisites

1. **Install PostgreSQL**
   - Download from: https://www.postgresql.org/download/windows/
   - During installation, remember the password you set for the `postgres` superuser
   - Default port: 5432
   - Make sure to install pgAdmin (optional but helpful for GUI management)

2. **Install Python PostgreSQL Driver**
   ```bash
   pip install psycopg2-binary
   ```

## Quick Setup (Automated)

Run the automated setup script:

```bash
setup_postgres_local.bat
```

This script will:
1. Create a local database named `scan2food_local`
2. Create a user `scan2food_dev` with password `dev_password_123`
3. Restore your backup from `dbbckup.sql`

## Manual Setup (If Automated Fails)

### Step 1: Create Database and User

Open Command Prompt or PowerShell and run:

```bash
# Connect to PostgreSQL
psql -U postgres

# In psql prompt, run these commands:
CREATE DATABASE scan2food_local;
CREATE USER scan2food_dev WITH PASSWORD 'dev_password_123';
ALTER ROLE scan2food_dev SET client_encoding TO 'utf8';
ALTER ROLE scan2food_dev SET default_transaction_isolation TO 'read committed';
ALTER ROLE scan2food_dev SET timezone TO 'Asia/Kolkata';
GRANT ALL PRIVILEGES ON DATABASE scan2food_local TO scan2food_dev;

# Connect to the new database
\c scan2food_local

# Grant schema permissions
GRANT ALL ON SCHEMA public TO scan2food_dev;

# Exit psql
\q
```

### Step 2: Restore Database Backup

```bash
psql -U scan2food_dev -d scan2food_local -f dbbckup.sql
```

Enter password when prompted: `dev_password_123`

### Step 3: Run Django Migrations

```bash
cd application\scan2food
python manage.py migrate
```

## Configuration

Your `.env` file has been updated with local PostgreSQL credentials:

```
DB_NAME=scan2food_local
DB_USER=scan2food_dev
DB_PASSWORD=dev_password_123
DB_HOST=localhost
DB_PORT=5432
```

## Separate Local and Production Databases

✅ **Local Database:**
- Name: `scan2food_local`
- User: `scan2food_dev`
- Password: `dev_password_123`

✅ **Production Database:**
- Name: `scan2food_db`
- User: `scan2food_user`
- Password: `scann2Food`

The databases are completely separate. Your local changes won't affect production.

## Troubleshooting

### Issue: "psql: command not found"

Add PostgreSQL to your PATH:
1. Find PostgreSQL bin directory (usually `C:\Program Files\PostgreSQL\16\bin`)
2. Add it to System Environment Variables PATH
3. Restart Command Prompt

### Issue: "FATAL: password authentication failed"

Make sure you're using the correct password:
- For `postgres` user: the password you set during installation
- For `scan2food_dev` user: `dev_password_123`

### Issue: "permission denied for schema public"

Run this as postgres superuser:
```bash
psql -U postgres -d scan2food_local -c "GRANT ALL ON SCHEMA public TO scan2food_dev;"
```

### Issue: Backup restore fails

The backup might be from a production database. Try:
1. Check if the backup file is valid: `head -n 50 dbbckup.sql`
2. Restore with more verbose output: `psql -U scan2food_dev -d scan2food_local -f dbbckup.sql -v ON_ERROR_STOP=1`

## Verify Setup

Test your database connection:

```bash
cd application\scan2food
python manage.py dbshell
```

This should connect you to PostgreSQL. Type `\dt` to list tables, then `\q` to exit.

## Next Steps

1. Delete old SQLite database (optional):
   ```bash
   del application\scan2food\db.sqlite3
   ```

2. Start your development server:
   ```bash
   run_local.bat
   ```

3. Test that everything works correctly

## Backup Your Local Database

To create a backup of your local database:

```bash
pg_dump -U scan2food_dev -d scan2food_local -f local_backup.sql
```

## Useful PostgreSQL Commands

```bash
# List all databases
psql -U postgres -l

# Connect to database
psql -U scan2food_dev -d scan2food_local

# Inside psql:
\dt              # List tables
\d table_name    # Describe table
\du              # List users
\l               # List databases
\q               # Quit
```
