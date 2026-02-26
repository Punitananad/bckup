# SQLite to PostgreSQL Migration Checklist

## ✅ Completed Steps

- [x] Updated `settings.py` to use PostgreSQL for both local and production
- [x] Updated `.env` with separate local database credentials
- [x] Created setup scripts for Windows
- [x] Verified `psycopg2-binary` is in requirements.txt

## 🔧 What You Need to Do

### 1. Install PostgreSQL (if not already installed)

Download and install PostgreSQL for Windows:
- URL: https://www.postgresql.org/download/windows/
- Remember the password you set for the `postgres` superuser
- Default port: 5432

### 2. Run the Setup Script

Open Command Prompt in your project directory and run:

```bash
setup_postgres_local.bat
```

This will:
- Create local database `scan2food_local`
- Create user `scan2food_dev` with password `dev_password_123`
- Restore your backup from `dbbckup.sql`

### 3. Install Python Dependencies

```bash
pip install psycopg2-binary
```

Or install all requirements:

```bash
pip install -r application\scan2food\requirements.txt
```

### 4. Verify Setup

Run the verification script:

```bash
python verify_postgres_setup.py
```

This will check if your database is properly configured and connected.

### 5. Run Django Migrations

```bash
cd application\scan2food
python manage.py migrate
```

### 6. Test Your Application

```bash
run_local.bat
```

Visit http://localhost:8000 and verify everything works.

### 7. Clean Up (Optional)

Delete the old SQLite database:

```bash
del application\scan2food\db.sqlite3
```

## 📊 Database Configuration Summary

### Local Development (Your Machine)
- **Database:** `scan2food_local`
- **User:** `scan2food_dev`
- **Password:** `dev_password_123`
- **Host:** `localhost`
- **Port:** `5432`

### Production (Server)
- **Database:** `scan2food_db`
- **User:** `scan2food_user`
- **Password:** `scann2Food`
- **Host:** `localhost` (on production server)
- **Port:** `5432`

## 🔒 Security Notes

1. **Separate Databases:** Local and production databases are completely separate
2. **Different Credentials:** Local uses `scan2food_dev`, production uses `scan2food_user`
3. **No Cross-Contamination:** Changes to local database won't affect production
4. **Backup Safety:** Your `dbbckup.sql` contains production data - keep it secure

## 🆘 Troubleshooting

### Problem: "psql: command not found"

**Solution:** Add PostgreSQL to your PATH
1. Find PostgreSQL bin directory: `C:\Program Files\PostgreSQL\16\bin`
2. Add to System Environment Variables PATH
3. Restart Command Prompt

### Problem: "password authentication failed"

**Solution:** Check your credentials
- For setup: Use `postgres` superuser password (set during installation)
- For app: Use `dev_password_123` (configured in `.env`)

### Problem: Backup restore fails

**Solution:** Try manual restore
```bash
psql -U postgres -c "DROP DATABASE IF EXISTS scan2food_local;"
psql -U postgres -c "CREATE DATABASE scan2food_local;"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE scan2food_local TO scan2food_dev;"
psql -U scan2food_dev -d scan2food_local -f dbbckup.sql
```

### Problem: "permission denied for schema public"

**Solution:** Grant schema permissions
```bash
psql -U postgres -d scan2food_local -c "GRANT ALL ON SCHEMA public TO scan2food_dev;"
```

## 📚 Additional Resources

- **PostgreSQL Documentation:** https://www.postgresql.org/docs/
- **Django PostgreSQL Notes:** https://docs.djangoproject.com/en/4.2/ref/databases/#postgresql-notes
- **Setup Guide:** See `POSTGRES_SETUP_GUIDE.md` for detailed instructions

## 🎯 Next Steps After Migration

1. Test all application features
2. Verify data integrity
3. Check that all queries work correctly
4. Update any SQLite-specific code (if any)
5. Create regular backup schedule for local database

## 💾 Backup Commands

### Create Local Backup
```bash
pg_dump -U scan2food_dev -d scan2food_local -f local_backup_$(date +%Y%m%d).sql
```

### Restore from Backup
```bash
psql -U scan2food_dev -d scan2food_local -f backup_file.sql
```

---

**Need Help?** Check `POSTGRES_SETUP_GUIDE.md` for detailed instructions.
