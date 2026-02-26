# 🚀 Setup PostgreSQL NOW - Simple Steps

## Your Situation

✅ PostgreSQL is installed (you have pgAdmin 4)
❌ PostgreSQL is not in your PATH (psql command not found)

## Easiest Solution (2 Steps)

### Step 1: Run This Command

Open Command Prompt in your project folder and run:

```bash
setup_postgres_easy.bat
```

**What it does:**
- Automatically finds your PostgreSQL installation
- Creates database `scan2food_local`
- Creates user `scan2food_dev`
- Restores your backup from `dbbckup.sql`

**What you need:**
- Your PostgreSQL `postgres` user password (you set this when installing PostgreSQL)

### Step 2: Install Python Dependencies

```bash
pip install psycopg2-binary
```

### Step 3: Start Your App

```bash
run_local.bat
```

That's it! 🎉

## Alternative: Use pgAdmin (If Script Fails)

If the script doesn't work, use pgAdmin 4:

### 1. Open pgAdmin 4
- Find it in your Start menu
- Enter your postgres password

### 2. Create Database
- Right-click "Databases" → "Create" → "Database"
- Name: `scan2food_local`
- Click "Save"

### 3. Create User
- Expand "Login/Group Roles"
- Right-click → "Create" → "Login/Group Role"
- **General tab:** Name = `scan2food_dev`
- **Definition tab:** Password = `dev_password_123`
- **Privileges tab:** Check "Can login?"
- Click "Save"

### 4. Grant Permissions
- Right-click `scan2food_local` database → "Query Tool"
- Paste and run:
```sql
GRANT ALL PRIVILEGES ON DATABASE scan2food_local TO scan2food_dev;
\c scan2food_local
GRANT ALL ON SCHEMA public TO scan2food_dev;
```

### 5. Restore Backup
- Right-click `scan2food_local` database → "Restore"
- Filename: Browse to your `dbbckup.sql` file
- Format: Plain
- Click "Restore"

### 6. Install Dependencies & Start
```bash
pip install psycopg2-binary
run_local.bat
```

## Verify It Works

Run this to check your setup:

```bash
python verify_postgres_setup.py
```

You should see:
- ✅ Connected successfully!
- Database statistics
- Table count

## Your Database Info

Already configured in your `.env` file:

```
Database: scan2food_local
User: scan2food_dev
Password: dev_password_123
Host: localhost
Port: 5432
```

## Need Help?

### Script says "Could not find PostgreSQL"
- Use pgAdmin method instead (see above)
- Or check: `C:\Program Files\PostgreSQL\16\bin\psql.exe` exists

### "Password authentication failed"
- Make sure you're entering the correct postgres password
- This is the password you set when you installed PostgreSQL

### Backup restore fails
- That's okay! The database structure might already exist
- Continue with the next steps

### Still stuck?
- See **SETUP_WITHOUT_PATH.md** for more options
- Or use pgAdmin 4 (GUI method above)

## Quick Commands Reference

```bash
# Setup database (automatic)
setup_postgres_easy.bat

# Install Python dependencies
pip install psycopg2-binary

# Verify setup
python verify_postgres_setup.py

# Start app
run_local.bat
```

---

**Ready?** Run `setup_postgres_easy.bat` now!
