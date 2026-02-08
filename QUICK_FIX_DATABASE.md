# 🔴 DATABASE CONNECTION ERROR - QUICK FIX

## Error Message
```
psycopg2.OperationalError: password authentication failed for user "guru"
```

## Root Cause
Your local PostgreSQL credentials don't match what's in `settings.py`:
- Database: `app`
- User: `guru`
- Password: `guru@2003`

---

## ✅ SOLUTION OPTIONS (Choose One)

### **Option 1: Use Your Existing PostgreSQL User (Easiest)**

1. Find your PostgreSQL username:
   ```cmd
   psql -U postgres -c "\du"
   ```
   Or try:
   ```cmd
   psql -U postgres
   ```

2. Update `settings.py` with your actual credentials:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'app',  # or create new database
           'USER': 'postgres',  # ← Change this to your username
           'PASSWORD': 'your_actual_password',  # ← Change this
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

---

### **Option 2: Create the 'guru' User (Match Server Config)**

1. Open PostgreSQL as superuser:
   ```cmd
   psql -U postgres
   ```

2. Run these commands:
   ```sql
   CREATE USER guru WITH PASSWORD 'guru@2003';
   CREATE DATABASE app OWNER guru;
   GRANT ALL PRIVILEGES ON DATABASE app TO guru;
   \q
   ```

3. Test connection:
   ```cmd
   psql -U guru -d app
   ```

---

### **Option 3: Use SQLite for Local Development (Simplest)**

If you don't need PostgreSQL locally, use SQLite:

1. Update `settings.py`:
   ```python
   # Comment out PostgreSQL
   # DATABASES = {
   #     'default': {
   #         'ENGINE': 'django.db.backends.postgresql',
   #         ...
   #     }
   # }
   
   # Use SQLite for local development
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': BASE_DIR / 'db.sqlite3',
       }
   }
   ```

2. Run migrations:
   ```cmd
   cd application\scan2food
   python manage.py migrate
   python manage.py createsuperuser
   ```

---

## 🔍 TROUBLESHOOTING

### Check if PostgreSQL is Running
```cmd
net start postgresql-x64-14
```
Or:
```cmd
sc query postgresql-x64-14
```

### Find PostgreSQL Service Name
```cmd
sc query | findstr postgres
```

### Test Connection Manually
```cmd
psql -U postgres
psql -U guru -d app
```

### Reset PostgreSQL Password (if needed)
1. Edit `pg_hba.conf` (usually in `C:\Program Files\PostgreSQL\14\data\`)
2. Change `md5` to `trust` temporarily
3. Restart PostgreSQL
4. Connect and change password:
   ```sql
   ALTER USER guru WITH PASSWORD 'guru@2003';
   ```
5. Change `trust` back to `md5`
6. Restart PostgreSQL

---

## 📝 RECOMMENDED FIX FOR LOCAL DEVELOPMENT

**Use Option 1 (Update settings.py with your credentials)**

1. Find your PostgreSQL username (usually `postgres`)
2. Update `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'scan2food_local',  # New database name
        'USER': 'postgres',  # Your actual username
        'PASSWORD': 'your_password',  # Your actual password
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

3. Create the database:
```cmd
psql -U postgres -c "CREATE DATABASE scan2food_local;"
```

4. Run migrations:
```cmd
cd application\scan2food
python manage.py migrate
python manage.py createsuperuser
```

5. Start server:
```cmd
run_local.bat
```

---

## ⚡ FASTEST FIX (If You Don't Care About Data)

Use SQLite - no PostgreSQL needed:

```cmd
cd application\scan2food
```

Edit `settings.py` - replace DATABASES with:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

Then:
```cmd
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Done! ✅

---

**Choose the option that works best for you and update accordingly.**
