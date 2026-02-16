# Quick Database Restore Guide

## Simple Steps to Restore Database from Local Backup

### Step 1: Upload Backup to Target Server
From your **Windows terminal**:
```cmd
scp C:\Users\punit\Downloads\app_backup_20260216_235624.sql root@165.22.219.111:/var/www/scan2food/
```

### Step 2: Restore Database on Server
**SSH into the server**:
```bash
ssh root@165.22.219.111
cd /var/www/scan2food
```

**Run these commands** (copy-paste all 3 lines together):
```bash
sudo -u postgres psql -c "DROP DATABASE IF EXISTS scan2food_db;"
sudo -u postgres psql -c "CREATE DATABASE scan2food_db OWNER scan2food_user;"
sudo -u postgres psql scan2food_db < /var/www/scan2food/app_backup_20260216_235624.sql
```

### Step 3: Fix Permissions
```bash
sudo -u postgres psql scan2food_db -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO scan2food_user;"
sudo -u postgres psql scan2food_db -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO scan2food_user;"
```

### Step 4: Restart Services
```bash
sudo systemctl restart gunicorn
sudo systemctl restart daphne
```

### Step 5: Verify
Check if services are running:
```bash
sudo systemctl status gunicorn
sudo systemctl status daphne
```

Visit your website to confirm it's working.

---

## That's It!

Just follow these 5 steps every time you need to restore a database backup.

## Important Notes:
- Current backup file: `app_backup_20260216_235624.sql` (Feb 16, 2026 - Latest backup)
- The backup file is already in `C:\Users\punit\Downloads\`
- Make sure you're connected to the correct server (165.22.219.111)
- If you need to fetch a new backup from remote server first, use the fetch_and_restore_db.py script
