# Quick Database Restore Guide

## Simple Steps to Restore Database from Another Server

### Step 1: Download Backup from Remote Server
From your **Windows terminal**:
```cmd
scp guru@scan2food.com:/home/guru/application/scan2food/media/backup_db/app_backup_13-Feb-2026.sql C:\Users\punit\Downloads\
```
(Replace the date with the actual backup file name)

### Step 2: Upload Backup to Target Server
From your **Windows terminal**:
```cmd
scp C:\Users\punit\Downloads\app_backup_13-Feb-2026.sql root@165.22.219.111:/var/www/scan2food/
```

### Step 3: Restore Database on Server
**SSH into the server**:
```bash
ssh root@165.22.219.111
cd /var/www/scan2food
```

**Run these commands** (copy-paste all 3 lines together):
```bash
sudo -u postgres psql -c "DROP DATABASE IF EXISTS scan2food_db;"
sudo -u postgres psql -c "CREATE DATABASE scan2food_db OWNER scan2food_user;"
sudo -u postgres psql scan2food_db < /var/www/scan2food/app_backup_13-Feb-2026.sql
```

### Step 4: Fix Permissions
```bash
sudo -u postgres psql scan2food_db -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO scan2food_user;"
sudo -u postgres psql scan2food_db -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO scan2food_user;"
```

### Step 5: Restart Services
```bash
sudo systemctl restart gunicorn
sudo systemctl restart daphne
```

### Step 6: Verify
Check if services are running:
```bash
sudo systemctl status gunicorn
sudo systemctl status daphne
```

Visit your website to confirm it's working.

---

## That's It!

Just follow these 6 steps every time you need to restore a database backup.

## Important Notes:
- Always replace `app_backup_13-Feb-2026.sql` with your actual backup filename
- The backup file will be in `C:\Users\punit\Downloads\` on your local machine
- Make sure you're connected to the correct server (165.22.219.111)
