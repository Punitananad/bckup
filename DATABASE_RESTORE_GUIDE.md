# Database Fetch and Restore Guide

This guide explains how to restore a database backup. There are two scenarios:

1. **Local Machine** - Fetch backup from server and restore locally (Windows/Mac/Linux)
2. **Production Server** - Restore backup directly on the server (Linux)

---

## Scenario 1: Restore on Local Machine (Fetch from Server)

Use this when you want to download a backup from the production server and restore it on your local development machine.

### Prerequisites

1. **SSH Access**: You must have SSH access to the production server (guru@scan2food.com)
2. **PostgreSQL**: PostgreSQL must be installed locally
3. **Python**: Python 3.x with `python-dotenv` package
4. **SCP**: SCP command-line tool (comes with SSH)

## Setup

### 1. Install Required Tools

**Windows:**
- Install PostgreSQL: https://www.postgresql.org/download/windows/
- Install Python: https://www.python.org/downloads/
- Install OpenSSH (for SCP): Usually comes with Windows 10/11

**Install Python dependencies:**
```bash
pip install python-dotenv
```

### 2. Configure Environment Variables

Create or update `application/scan2food/.env` file with your local database credentials:

```env
DB_NAME=scan2food_db
DB_USER=your_local_db_user
DB_PASSWORD=your_local_db_password
DB_HOST=localhost
DB_PORT=5432
```

### 3. Ensure PostgreSQL User Has Permissions

Your PostgreSQL user needs CREATEDB permission:

```sql
psql -U postgres
ALTER USER your_local_db_user CREATEDB;
```

## Usage

### Method 1: Using Python Script Directly

```bash
python fetch_and_restore_db.py <backup_filename>
```

**Example:**
```bash
python fetch_and_restore_db.py app_backup_13-Feb-2026.sql
```

Or with python3:
```bash
python3 fetch_and_restore_db.py app_backup_13-Feb-2026.sql
```

### Method 2: Using Windows Batch File

Double-click `fetch_and_restore_db.bat` or run from command prompt:

```cmd
fetch_and_restore_db.bat app_backup_13-Feb-2026.sql
```

---

## Scenario 2: Restore on Production Server (Direct Restore)

Use this when you're already on the production server and want to restore from a backup file that's already on the server.

### Prerequisites

1. SSH access to the server
2. Backup file exists on the server
3. PostgreSQL installed and running

### Usage

**SSH into the server:**
```bash
ssh root@165.22.219.111
# or
ssh guru@scan2food.com
```

**Navigate to the project directory:**
```bash
cd /var/www/scan2food
```

**Run the restore script:**
```bash
python3 restore_db_from_local.py app_backup_13-Feb-2026.sql
```

The script will automatically search for the backup file in these locations:
- `/home/guru/application/scan2food/media/backup_db/`
- `/var/www/scan2food/application/scan2food/backupScript/backups/`
- `./application/scan2food/backupScript/backups/`
- `./backups/`

**Or provide the full path:**
```bash
python3 restore_db_from_local.py /home/guru/application/scan2food/media/backup_db/app_backup_13-Feb-2026.sql
```

### After Restore on Server

After successfully restoring on the production server:

```bash
# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart daphne

# Check logs
sudo journalctl -u gunicorn -f
sudo journalctl -u daphne -f
```

---

## What the Scripts Do (Local Machine)

The script performs the following steps automatically:

1. **Fetches Backup from Server**
   - Connects to `guru@scan2food.com` via SCP
   - Downloads backup from `/home/guru/application/scan2food/media/backup_db/`
   - Saves to `application/scan2food/backupScript/backups/`

2. **Drops Current Database**
   - Drops the existing local database (if it exists)

3. **Creates New Database**
   - Creates a fresh empty database

4. **Restores from Backup**
   - Imports the SQL backup file into the new database

## Remote Server Backup Location

**Server:** guru@scan2food.com  
**Path:** `/home/guru/application/scan2food/media/backup_db/`

## Local Backup Storage

Downloaded backups are stored in:
```
application/scan2food/backupScript/backups/
```

## Troubleshooting

### SSH/SCP Connection Issues

If you get SSH connection errors:

1. **Test SSH connection first:**
   ```bash
   ssh guru@scan2food.com
   ```

2. **Check if backup file exists on server:**
   ```bash
   ssh guru@scan2food.com "ls -la /home/guru/application/scan2food/media/backup_db/"
   ```

3. **Manually download using SCP:**
   ```bash
   scp guru@scan2food.com:/home/guru/application/scan2food/media/backup_db/app_backup_13-Feb-2026.sql application/scan2food/backupScript/backups/
   ```

### PostgreSQL Permission Issues

If you get "permission denied" errors:

```sql
-- Connect as postgres superuser
psql -U postgres

-- Grant CREATEDB permission
ALTER USER your_local_db_user CREATEDB;

-- Grant all privileges on database
GRANT ALL PRIVILEGES ON DATABASE scan2food_db TO your_local_db_user;
```

### Database Already Exists Error

The script automatically drops the existing database. If this fails:

```bash
# Manually drop the database
dropdb -U your_local_db_user scan2food_db

# Then run the script again
python fetch_and_restore_db.py app_backup_13-Feb-2026.sql
```

### Encoding Issues

If you encounter encoding errors during restore:

1. Ensure the backup file is UTF-8 encoded
2. Check PostgreSQL locale settings:
   ```sql
   SHOW SERVER_ENCODING;
   ```

## Manual Process (If Script Fails)

If the automated script fails, you can perform the steps manually:

### Step 1: Download Backup
```bash
scp guru@scan2food.com:/home/guru/application/scan2food/media/backup_db/app_backup_13-Feb-2026.sql C:\Users\punit\Downloads\
```

### Step 2: Drop Database
```bash
dropdb -U your_local_db_user scan2food_db
```

### Step 3: Create Database
```bash
createdb -U your_local_db_user scan2food_db
```

### Step 4: Restore Backup
```bash
psql -U your_local_db_user scan2food_db < C:\Users\punit\Downloads\app_backup_13-Feb-2026.sql
```

## After Restore

After successfully restoring the database:

1. **Restart Django Application**
   ```bash
   python application/scan2food/manage.py runserver
   ```

2. **Run Migrations (if needed)**
   ```bash
   python application/scan2food/manage.py migrate
   ```

3. **Test the Application**
   - Login to admin panel
   - Check if data is loaded correctly
   - Test key functionality

## Security Notes

- The script uses environment variables for database credentials
- Never commit `.env` file with real credentials to Git
- Keep SSH keys secure
- Backup files may contain sensitive data - handle with care

## Available Backup Files

To see available backup files on the server:

```bash
ssh guru@scan2food.com "ls -lh /home/guru/application/scan2food/media/backup_db/"
```

## Script Locations

### For Local Machine (Fetch from Server)
- **Python Script:** `fetch_and_restore_db.py`
- **Windows Batch:** `fetch_and_restore_db.bat`

### For Production Server (Direct Restore)
- **Python Script:** `restore_db_from_local.py`

### Documentation
- **This Guide:** `DATABASE_RESTORE_GUIDE.md`

## Support

If you encounter issues:
1. Check the error messages carefully
2. Verify SSH access to the server
3. Ensure PostgreSQL is running locally
4. Check database credentials in `.env` file
5. Review the troubleshooting section above
