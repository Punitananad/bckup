# ✅ SQLite Configured for Local Development

## What Was Done

Your Django project has been configured to use SQLite instead of PostgreSQL for local development.

### Changes Made

**File:** `application/scan2food/theatreApp/settings.py`

```python
# BEFORE (PostgreSQL - causing authentication error)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'app',
        'USER': 'guru',
        'PASSWORD': 'guru@2003',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# AFTER (SQLite - works out of the box)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

---

## 🚀 Next Steps

### Step 1: Create the Database (Run Once)

From the project root directory:

```cmd
setup_sqlite.bat
```

This will:
1. Run all migrations
2. Create the SQLite database file
3. Prompt you to create a superuser (admin account)

**Or manually:**
```cmd
cd application\scan2food
python manage.py migrate
python manage.py createsuperuser
```

---

### Step 2: Start the Development Server

```cmd
run_local.bat
```

**Or manually:**
```cmd
cd application\scan2food
python manage.py runserver
```

---

### Step 3: Access Your Application

Open your browser and visit:
- **Main App:** http://localhost:8000
- **Admin Panel:** http://localhost:8000/admin/
- **Theatre:** http://localhost:8000/theatre/

---

## ✅ Benefits of SQLite for Local Development

| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| **Setup** | Zero configuration | Requires installation & setup |
| **Speed** | Fast for development | Slower for small datasets |
| **File-based** | Single `db.sqlite3` file | Server process required |
| **Reset** | Just delete the file | Need to drop/recreate database |
| **Portability** | Copy file = copy database | Need dump/restore |
| **Perfect for** | Local development | Production |

---

## 📝 What's Different from Production?

### Local Development (SQLite)
- Database: `db.sqlite3` file
- No server process needed
- Perfect for testing and development
- Easy to reset and start fresh

### Production (PostgreSQL)
- Database: PostgreSQL server
- Better for concurrent users
- Better for large datasets
- Production-ready features

**Note:** The PostgreSQL configuration is still in `settings.py` (commented out) for when you deploy to production.

---

## 🔄 Common Operations

### Reset Database (Start Fresh)
```cmd
cd application\scan2food
del db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### View Database
Use a SQLite browser like:
- DB Browser for SQLite (https://sqlitebrowser.org/)
- Or VS Code extension: SQLite Viewer

### Backup Database
```cmd
copy application\scan2food\db.sqlite3 backup_db.sqlite3
```

### Restore Database
```cmd
copy backup_db.sqlite3 application\scan2food\db.sqlite3
```

---

## 🐛 Troubleshooting

### Error: "no such table"
**Solution:** Run migrations
```cmd
cd application\scan2food
python manage.py migrate
```

### Error: "database is locked"
**Solution:** Close any other processes accessing the database
- Close DB Browser if open
- Stop any other Django servers
- Restart the server

### Want to Switch Back to PostgreSQL?
Edit `settings.py` and uncomment the PostgreSQL configuration:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'app',
        'USER': 'your_username',  # Update this
        'PASSWORD': 'your_password',  # Update this
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## 📊 Database File Location

Your SQLite database will be created at:
```
application/scan2food/db.sqlite3
```

This file contains all your:
- Users and authentication
- Theatre data
- Orders and payments
- All application data

**Important:** Add `db.sqlite3` to `.gitignore` - don't commit it to git!

---

## ✅ Summary

**What's Working Now:**
- ✅ Database configured (SQLite)
- ✅ Static files configured
- ✅ Admin errors fixed
- ✅ Cookie settings for localhost
- ✅ Ready for development

**Next Steps:**
1. Run `setup_sqlite.bat` (one time)
2. Run `run_local.bat` (every time you develop)
3. Start coding!

---

**Everything is ready for local development! 🚀**
