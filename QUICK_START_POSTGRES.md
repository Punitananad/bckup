# 🚀 Quick Start: PostgreSQL Migration

## TL;DR - Run These Commands

```bash
# 1. Install PostgreSQL from https://www.postgresql.org/download/windows/

# 2. Run setup script
setup_postgres_local.bat

# 3. Verify setup
python verify_postgres_setup.py

# 4. Start your app
run_local.bat
```

## What Changed?

### ✅ Before (SQLite)
- Local: SQLite database file (`db.sqlite3`)
- Production: PostgreSQL database

### ✅ After (PostgreSQL Everywhere)
- Local: PostgreSQL database (`scan2food_local`)
- Production: PostgreSQL database (`scan2food_db`)

## Why This Is Better

1. **Same Database Engine:** No surprises when deploying to production
2. **Better Performance:** PostgreSQL handles concurrent connections better
3. **Advanced Features:** Full-text search, JSON fields, better indexing
4. **Separate Databases:** Local (`scan2food_local`) and production (`scan2food_db`) are completely isolated

## Your Database Credentials

### Local Development
```
Database: scan2food_local
User: scan2food_dev
Password: dev_password_123
Host: localhost
Port: 5432
```

### Production (Unchanged)
```
Database: scan2food_db
User: scan2food_user
Password: scann2Food
Host: localhost
Port: 5432
```

## Files Created

1. **setup_postgres_local.bat** - Automated setup script
2. **restore_backup.bat** - Restore database from backup
3. **verify_postgres_setup.py** - Check if everything works
4. **POSTGRES_SETUP_GUIDE.md** - Detailed documentation
5. **MIGRATION_CHECKLIST.md** - Step-by-step checklist

## Files Modified

1. **application/scan2food/theatreApp/settings.py** - Now uses PostgreSQL for all environments
2. **application/scan2food/.env** - Updated with local database credentials

## Need Help?

- **Detailed Guide:** See `POSTGRES_SETUP_GUIDE.md`
- **Step-by-Step:** See `MIGRATION_CHECKLIST.md`
- **Troubleshooting:** Both guides have troubleshooting sections

## Common Issues

### "psql: command not found"
Add PostgreSQL to PATH: `C:\Program Files\PostgreSQL\16\bin`

### "password authentication failed"
Use the password you set during PostgreSQL installation

### "database does not exist"
Run `setup_postgres_local.bat` to create it

---

**Ready to start?** Run `setup_postgres_local.bat` now!
