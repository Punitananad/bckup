# Setup PostgreSQL Without PATH

Your PostgreSQL is installed but not in your system PATH. Here are two ways to fix this:

## Option 1: Quick Setup (Recommended)

Run this script - it will find PostgreSQL automatically:

```bash
setup_postgres_easy.bat
```

This script:
- Automatically finds your PostgreSQL installation
- Creates the database and user
- Restores your backup
- Works without adding PostgreSQL to PATH

## Option 2: Add PostgreSQL to PATH (Better Long-term)

### Automatic Helper

```bash
add_postgres_to_path.bat
```

This will show you the exact path and instructions.

### Manual Steps

1. **Find PostgreSQL Location**
   - Usually: `C:\Program Files\PostgreSQL\16\bin`
   - Or: `C:\Program Files\PostgreSQL\15\bin`

2. **Add to PATH**
   - Press `Windows + S` and search "Environment Variables"
   - Click "Edit the system environment variables"
   - Click "Environment Variables" button
   - Under "System variables", find "Path" and click "Edit"
   - Click "New"
   - Paste: `C:\Program Files\PostgreSQL\16\bin` (adjust version number)
   - Click "OK" on all windows

3. **Restart Command Prompt**
   - Close all Command Prompt windows
   - Open a new one
   - Test: `psql --version`

## Option 3: Use pgAdmin (GUI)

Since you have pgAdmin 4 installed, you can use it:

1. **Open pgAdmin 4** (from Start menu)

2. **Connect to PostgreSQL**
   - Enter your postgres password

3. **Create Database**
   - Right-click "Databases" → "Create" → "Database"
   - Name: `scan2food_local`
   - Owner: postgres
   - Save

4. **Create User**
   - Right-click "Login/Group Roles" → "Create" → "Login/Group Role"
   - General tab → Name: `scan2food_dev`
   - Definition tab → Password: `dev_password_123`
   - Privileges tab → Check "Can login?"
   - Save

5. **Grant Permissions**
   - Right-click `scan2food_local` database → "Query Tool"
   - Run this SQL:
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE scan2food_local TO scan2food_dev;
   GRANT ALL ON SCHEMA public TO scan2food_dev;
   ```

6. **Restore Backup**
   - Right-click `scan2food_local` database → "Restore"
   - Format: Custom or tar
   - Filename: Browse to `dbbckup.sql`
   - Click "Restore"

## After Setup

Regardless of which method you used, run:

```bash
# Install Python dependencies
pip install psycopg2-binary

# Verify setup
python verify_postgres_setup.py

# Start your app
run_local.bat
```

## Quick Reference

Your database credentials (already in `.env`):
```
DB_NAME=scan2food_local
DB_USER=scan2food_dev
DB_PASSWORD=dev_password_123
DB_HOST=localhost
DB_PORT=5432
```

## Troubleshooting

### "Could not find PostgreSQL"
Check these locations:
- `C:\Program Files\PostgreSQL\16\bin`
- `C:\Program Files\PostgreSQL\15\bin`
- `C:\Program Files\PostgreSQL\14\bin`

### "Password authentication failed"
Make sure you're using:
- For setup: Your postgres superuser password (set during installation)
- For app: `dev_password_123` (configured in `.env`)

### Still Having Issues?
Use pgAdmin 4 (Option 3) - it's the most reliable method when PATH isn't configured.
