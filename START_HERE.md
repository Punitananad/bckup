# 🎯 START HERE - PostgreSQL Migration Guide

Welcome! Your Scan2Food application has been migrated from SQLite to PostgreSQL for local development.

## 🚀 Quick Setup (Choose One)

### Option 1: Easy Setup (Recommended - Works Without PATH)
```bash
setup_postgres_easy.bat
```
This automatically finds PostgreSQL and sets everything up.

### Option 2: Add PostgreSQL to PATH First
```bash
# 1. Add to PATH (one-time setup)
add_postgres_to_path.bat

# 2. Restart Command Prompt

# 3. Run full setup
first_time_setup.bat
```

### Option 3: Use pgAdmin GUI
See **SETUP_WITHOUT_PATH.md** for GUI instructions.

## 📚 Documentation Index

### Getting Started
1. **START_HERE.md** ← You are here
2. **QUICK_START_POSTGRES.md** - Quick overview
3. **README_POSTGRES_MIGRATION.md** - Complete guide

### Detailed Documentation
4. **POSTGRES_SETUP_GUIDE.md** - Step-by-step setup
5. **MIGRATION_CHECKLIST.md** - Migration checklist
6. **DATABASE_ARCHITECTURE.md** - How it all works

### Reference
7. **POSTGRES_MIGRATION_SUMMARY.md** - What changed

## 🎬 Setup Scripts

| Script | Purpose |
|--------|---------|
| `first_time_setup.bat` | Complete automated setup |
| `check_postgres_installed.bat` | Check if PostgreSQL is installed |
| `setup_postgres_local.bat` | Create database and restore backup |
| `restore_backup.bat` | Restore database from backup |
| `verify_postgres_setup.py` | Verify database connection |
| `run_local.bat` | Start development server |

## 🗄️ Database Info

### Your Local Database
```
Database: scan2food_local
User: scan2food_dev
Password: dev_password_123
Host: localhost
Port: 5432
```

### Production Database (Unchanged)
```
Database: scan2food_db
User: scan2food_user
Password: scann2Food
Host: localhost (on server)
Port: 5432
```

**Important:** These are separate databases. Local changes won't affect production!

## ✅ What Changed?

### Before
- **Local:** SQLite database file
- **Production:** PostgreSQL database

### After
- **Local:** PostgreSQL database (scan2food_local)
- **Production:** PostgreSQL database (scan2food_db)

### Why?
- Same database engine everywhere
- Better performance and features
- Test production-like queries locally
- Separate databases for safety

## 🎯 Your Next Steps

1. **Install PostgreSQL** (if not already installed)
   - Download: https://www.postgresql.org/download/windows/
   - Remember the password for 'postgres' user

2. **Run Setup**
   ```bash
   first_time_setup.bat
   ```

3. **Start Developing**
   ```bash
   run_local.bat
   ```

4. **Visit Your App**
   - http://localhost:8000

## 🆘 Need Help?

### Quick Answers
- **PostgreSQL not found?** Add to PATH: `C:\Program Files\PostgreSQL\16\bin`
- **Setup failed?** Check PostgreSQL service is running
- **Connection error?** Run `verify_postgres_setup.py` for diagnostics
- **Need to restore backup again?** Run `restore_backup.bat`

### Detailed Help
- See **POSTGRES_SETUP_GUIDE.md** for troubleshooting
- Check **README_POSTGRES_MIGRATION.md** for FAQ

## 📖 Recommended Reading Order

1. **START_HERE.md** (this file) - Overview
2. **QUICK_START_POSTGRES.md** - Quick start
3. **DATABASE_ARCHITECTURE.md** - Understand the setup
4. **POSTGRES_SETUP_GUIDE.md** - Detailed instructions (if needed)

## 🔐 Security Notes

- Local and production databases are completely separate
- Different credentials for each environment
- `.env` file is not committed to git
- Database backups are not committed to git
- Keep `dbbckup.sql` secure (contains production data)

## 💡 Tips

- Use `verify_postgres_setup.py` to check your setup anytime
- Create backups before major changes: `pg_dump -U scan2food_dev -d scan2food_local -f backup.sql`
- Connect to database: `psql -U scan2food_dev -d scan2food_local`
- List tables in psql: `\dt`

## 🎉 Ready to Start?

Run this command now:

```bash
first_time_setup.bat
```

Or if you prefer manual control:

```bash
check_postgres_installed.bat
```

---

**Questions?** Check the documentation files listed above or the troubleshooting sections.

**Everything working?** Delete this file and the other migration docs to clean up your workspace.
