# 🗄️ PostgreSQL Setup Guide for Production

## 🎯 Overview

Your production server will use PostgreSQL with **NEW secure credentials** (not the old compromised ones).

---

## 📋 Step-by-Step Setup

### STEP 1: Install PostgreSQL on Server

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Check status
sudo systemctl status postgresql
```

---

### STEP 2: Create NEW Database and User

**⚠️ IMPORTANT:** Use NEW credentials, NOT the old ones!

**Old credentials (COMPROMISED - DO NOT USE):**
- ❌ User: `guru`
- ❌ Password: `guru@2003`
- ❌ Database: `app`

**Create NEW secure credentials:**

```bash
# Login to PostgreSQL as postgres user
sudo -u postgres psql

# You'll see: postgres=#
```

**Run these commands in PostgreSQL:**

```sql
-- Create NEW database
CREATE DATABASE scan2food_db;

-- Create NEW user with STRONG password
CREATE USER scan2food_user WITH PASSWORD 'YourStrongPassword123!@#';

-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE scan2food_db TO scan2food_user;

-- Grant schema permissions (PostgreSQL 15+)
\c scan2food_db
GRANT ALL ON SCHEMA public TO scan2food_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO scan2food_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO scan2food_user;

-- Exit
\q
```

**Generate a strong password:**
```bash
# Use this to generate a random strong password
openssl rand -base64 32
```

---

### STEP 3: Configure PostgreSQL for Remote Access (if needed)

**Edit PostgreSQL config:**
```bash
sudo nano /etc/postgresql/15/main/postgresql.conf
```

**Find and change:**
```
listen_addresses = 'localhost'
```

**Edit pg_hba.conf:**
```bash
sudo nano /etc/postgresql/15/main/pg_hba.conf
```

**Add this line (for local connections):**
```
local   scan2food_db    scan2food_user                          md5
host    scan2food_db    scan2food_user    127.0.0.1/32          md5
```

**Restart PostgreSQL:**
```bash
sudo systemctl restart postgresql
```

---

### STEP 4: Test Database Connection

```bash
# Test connection
psql -U scan2food_user -d scan2food_db -h localhost

# If successful, you'll see:
# scan2food_db=>

# Exit
\q
```

---

### STEP 5: Set Environment Variables on Server

**Create environment file:**
```bash
sudo nano /etc/environment
```

**Add these lines:**
```bash
DJANGO_ENV=production
DB_NAME=scan2food_db
DB_USER=scan2food_user
DB_PASSWORD=YourStrongPassword123!@#
DB_HOST=localhost
DB_PORT=5432
```

**Or create .env file in project directory:**
```bash
cd /var/www/scan2food/application/scan2food
nano .env
```

**Add:**
```env
DJANGO_ENV=production
DB_NAME=scan2food_db
DB_USER=scan2food_user
DB_PASSWORD=YourStrongPassword123!@#
DB_HOST=localhost
DB_PORT=5432
```

**Install python-dotenv:**
```bash
pip install python-dotenv
```

**Update settings.py to load .env:**
```python
# At the top of settings.py
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
```

---

### STEP 6: Run Django Migrations

```bash
cd /var/www/scan2food/application/scan2food

# Activate virtual environment
source venv/bin/activate

# Set environment variable
export DJANGO_ENV=production

# Run migrations
python manage.py migrate

# You should see:
# Running migrations:
#   Applying contenttypes.0001_initial... OK
#   Applying auth.0001_initial... OK
#   ... etc
```

---

### STEP 7: Create Superuser

```bash
python manage.py createsuperuser

# Enter:
# Username: punit
# Email: punitanand146@gmail.com
# Password: [your NEW strong password]
# Password (again): [same password]
```

---

### STEP 8: Backup Old Database and Migrate Data

**If you have data from old server:**

#### Option A: Dump from old server (if you have access)

**On OLD server:**
```bash
# Dump data to JSON (safer for cross-database migration)
python manage.py dumpdata --natural-foreign --natural-primary \
  --exclude contenttypes --exclude auth.Permission \
  --exclude admin.logentry --exclude sessions.session \
  > full_backup.json

# Or dump specific apps
python manage.py dumpdata theatre > theatre_data.json
python manage.py dumpdata adminPortal > adminportal_data.json
```

**Transfer to NEW server:**
```bash
scp full_backup.json user@new_server:/var/www/scan2food/
```

**On NEW server:**
```bash
# Load data
python manage.py loaddata full_backup.json
```

#### Option B: PostgreSQL dump (if old server used PostgreSQL)

**On OLD server:**
```bash
pg_dump -U guru -d app -h localhost > old_database.sql
```

**On NEW server:**
```bash
# Load into new database
psql -U scan2food_user -d scan2food_db -h localhost < old_database.sql
```

---

### STEP 9: Verify Database

```bash
# Check tables were created
psql -U scan2food_user -d scan2food_db -h localhost

# List tables
\dt

# You should see tables like:
# theatre_food
# theatre_order
# adminportal_paymentgateway
# etc.

# Check data
SELECT COUNT(*) FROM theatre_food;
SELECT COUNT(*) FROM theatre_order;

# Exit
\q
```

---

### STEP 10: Update Payment Gateway Credentials in Database

**After migration, you MUST update payment gateway credentials:**

```bash
# Login to Django admin
# http://YOUR_SERVER_IP:8000/admin/

# Go to: Admin Portal → Payment Gateways
# Delete old entries or update with NEW credentials
```

**Or via Django shell:**
```bash
python manage.py shell
```

```python
from adminPortal.models import PaymentGateway

# Delete all old payment gateways
PaymentGateway.objects.all().delete()

# Add new Razorpay
PaymentGateway.objects.create(
    name='Razorpay',
    gateway_key='rzp_live_YOUR_NEW_KEY',
    gateway_secret='YOUR_NEW_SECRET',
    is_active=True
)

# Add new Cashfree
PaymentGateway.objects.create(
    name='Cashfree',
    gateway_key='YOUR_NEW_APP_ID',
    gateway_secret='YOUR_NEW_SECRET',
    is_active=True
)

# Exit
exit()
```

---

## 🔒 Security Best Practices

### 1. Secure PostgreSQL

```bash
# Edit postgresql.conf
sudo nano /etc/postgresql/15/main/postgresql.conf

# Set strong password encryption
password_encryption = scram-sha-256

# Limit connections
max_connections = 100
```

### 2. Regular Backups

**Create backup script:**
```bash
sudo nano /usr/local/bin/backup_scan2food.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/scan2food"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U scan2food_user -d scan2food_db > $BACKUP_DIR/db_$DATE.sql

# Compress
gzip $BACKUP_DIR/db_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: db_$DATE.sql.gz"
```

**Make executable:**
```bash
sudo chmod +x /usr/local/bin/backup_scan2food.sh
```

**Add to crontab:**
```bash
crontab -e

# Add this line (backup daily at 2 AM)
0 2 * * * /usr/local/bin/backup_scan2food.sh
```

### 3. Monitor Database

```bash
# Check database size
psql -U scan2food_user -d scan2food_db -c "SELECT pg_size_pretty(pg_database_size('scan2food_db'));"

# Check active connections
psql -U scan2food_user -d scan2food_db -c "SELECT count(*) FROM pg_stat_activity;"

# Check slow queries
psql -U scan2food_user -d scan2food_db -c "SELECT query, calls, total_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

---

## 🆘 Troubleshooting

### Connection Error: "FATAL: password authentication failed"

**Check:**
1. Password is correct
2. User exists: `sudo -u postgres psql -c "\du"`
3. Database exists: `sudo -u postgres psql -c "\l"`
4. pg_hba.conf is configured correctly

### Error: "permission denied for schema public"

**Fix:**
```sql
sudo -u postgres psql scan2food_db
GRANT ALL ON SCHEMA public TO scan2food_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO scan2food_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO scan2food_user;
```

### Django can't connect to database

**Check environment variables:**
```bash
echo $DJANGO_ENV
echo $DB_NAME
echo $DB_USER
```

**Test connection manually:**
```bash
psql -U scan2food_user -d scan2food_db -h localhost
```

---

## 📝 Credentials Checklist

**Save these securely:**

```
=== PostgreSQL Production Credentials ===
Database Name: scan2food_db
Username: scan2food_user
Password: [your strong password]
Host: localhost
Port: 5432

=== OLD CREDENTIALS (DO NOT USE) ===
❌ Database: app
❌ Username: guru
❌ Password: guru@2003
```

---

## ✅ Verification Checklist

- [ ] PostgreSQL installed and running
- [ ] New database `scan2food_db` created
- [ ] New user `scan2food_user` created with strong password
- [ ] Environment variables set
- [ ] Django migrations completed successfully
- [ ] Superuser created
- [ ] Data migrated from old server (if applicable)
- [ ] Payment gateway credentials updated
- [ ] Backup script configured
- [ ] Database connection tested

---

## 🚀 Next Steps

After PostgreSQL is set up:

1. ✅ Configure payment gateways in admin
2. ✅ Test all payment flows
3. ✅ Update webhook URLs
4. ✅ Monitor database performance
5. ✅ Set up regular backups

---

**Your database is now secure with NEW credentials that old developer doesn't know!**
