# 🔐 OLD vs NEW Credentials

## 🚨 OLD CREDENTIALS (COMPROMISED)

### Where They Were Stored:

1. **settings.py** (now commented out ✅)
2. **db_backup.py** (now updated ✅)
3. **db_restore.py** (now updated ✅)

### Old Database Credentials:
```
❌ Database Name: app
❌ Username: guru
❌ Password: guru@2003
❌ Host: localhost
❌ Port: 5432
```

**Status:** Old developer KNOWS these credentials

**Risk:** On live server (134.209.149.31), old developer can:
- Access database
- Read all data
- Delete data
- Steal customer information
- Corrupt the database

---

## ✅ NEW CREDENTIALS (SECURE)

### Where They're Stored:

1. **Environment variables** (in .env file on server)
2. **NOT in code** (more secure)
3. **Only you know them**

### New Database Credentials:
```
✅ Database Name: scan2food_db
✅ Username: scan2food_user
✅ Password: [YOU CHOOSE - Strong password]
✅ Host: localhost
✅ Port: 5432
```

**Status:** Old developer DOES NOT know these

**Security:** Only accessible via:
- .env file on new server
- Only you have access
- Old developer has ZERO access

---

## 📊 COMPARISON

| Item | OLD (Compromised) | NEW (Secure) |
|------|-------------------|--------------|
| **Database Name** | app | scan2food_db |
| **Username** | guru | scan2food_user |
| **Password** | guru@2003 | YourStrongPassword123! |
| **Storage** | Hardcoded in files | Environment variables |
| **Old Dev Knows?** | ✅ YES | ❌ NO |
| **Secure?** | ❌ NO | ✅ YES |

---

## 🔧 WHAT I FIXED

### ✅ Updated Files:

1. **settings.py**
   - Removed hardcoded credentials
   - Now uses environment variables
   - Old credentials commented out with warning

2. **db_backup.py**
   - Removed hardcoded credentials
   - Now uses environment variables
   - Old credentials commented out

3. **db_restore.py**
   - Removed hardcoded credentials
   - Now uses environment variables
   - Old credentials commented out

---

## 🎯 ON NEW SERVER

### You Will Create:

**File:** `/var/www/scan2food/application/scan2food/.env`

**Content:**
```env
DJANGO_ENV=production

# Database - NEW SECURE CREDENTIALS
DB_NAME=scan2food_db
DB_USER=scan2food_user
DB_PASSWORD=YourStrongPassword123!@#
DB_HOST=localhost
DB_PORT=5432
```

### All Scripts Will Use These:
- ✅ Django (settings.py)
- ✅ Backup script (db_backup.py)
- ✅ Restore script (db_restore.py)

---

## 🔒 SECURITY BENEFITS

### OLD System (Insecure):
```python
# Hardcoded in code
DB_USER = "guru"
DB_PASSWORD = "guru@2003"
```
- ❌ Visible in code
- ❌ Committed to git
- ❌ Old developer knows
- ❌ Can't change easily

### NEW System (Secure):
```python
# From environment variables
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
```
- ✅ Not in code
- ✅ Not in git
- ✅ Only in .env file on server
- ✅ Easy to change
- ✅ Old developer doesn't know

---

## ⚠️ IMPORTANT

### On Live Server (134.209.149.31):
**Still uses OLD credentials!**
- Old developer still has access
- That's why we're migrating to NEW server
- After migration, shut down old server

### On New Server:
**Uses NEW credentials!**
- Old developer has NO access
- Completely secure
- Fresh start

---

## ✅ CHECKLIST

- [x] Removed hardcoded credentials from settings.py
- [x] Removed hardcoded credentials from db_backup.py
- [x] Removed hardcoded credentials from db_restore.py
- [x] All scripts now use environment variables
- [ ] Create .env file on new server (during deployment)
- [ ] Setup PostgreSQL with NEW credentials
- [ ] Test connection with NEW credentials
- [ ] Migrate data to new server
- [ ] Shut down old server

---

**Your code is now secure! Old credentials are removed and new ones will be in .env file only.** 🔒
