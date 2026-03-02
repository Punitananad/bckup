# Automated Database Backup Setup Guide

## Overview
This guide sets up automated daily backups of your PostgreSQL database at 4:00 AM every morning.

## Files Created
1. `application/scan2food/backupScript/automated_backup.py` - Main backup script
2. `setup_backup_cron.sh` - Cron job setup script

## Installation Steps

### On Your Deployment Server (165.22.219.111)

1. **Upload the files to the server:**
   ```bash
   cd /var/www/scan2food
   git pull origin main
   ```

2. **Make the setup script executable:**
   ```bash
   chmod +x setup_backup_cron.sh
   ```

3. **Run the setup script:**
   ```bash
   sudo bash setup_backup_cron.sh
   ```

   This will:
   - Create log directory at `/var/log/scan2food/`
   - Make the backup script executable
   - Add a cron job to run at 4:00 AM daily
   - Run a test backup to verify everything works

## Backup Details

- **Schedule:** Daily at 4:00 AM
- **Location:** `/var/www/scan2food/application/scan2food/media/backup_db/`
- **Naming Format:** `app_backup_DD-MMM-YYYY.sql` (e.g., `app_backup_07-Feb-2026.sql`)
- **Retention:** Automatically deletes backups older than 30 days
- **Log File:** `/var/log/scan2food/backup.log`

## Verification Commands

### Check if cron job is installed:
```bash
crontab -l
```

You should see:
```
0 4 * * * cd /var/www/scan2food/application/scan2food && /usr/bin/python3 /var/www/scan2food/application/scan2food/backupScript/automated_backup.py >> /var/log/scan2food/backup.log 2>&1
```

### View backup logs:
```bash
tail -f /var/log/scan2food/backup.log
```

### List existing backups:
```bash
ls -lh /var/www/scan2food/application/scan2food/media/backup_db/
```

### Test backup manually:
```bash
cd /var/www/scan2food/application/scan2food
python3 backupScript/automated_backup.py
```

## Accessing Backups via Web Interface

Visit: `https://scan2food.com/admin-portal/get-db-files`

You'll see all backups listed with:
- File name
- Size (in MB)
- Date
- Download button

## Troubleshooting

### If backup fails:

1. **Check PostgreSQL credentials:**
   ```bash
   cat /var/www/scan2food/application/scan2food/.env
   ```

2. **Test PostgreSQL connection:**
   ```bash
   psql -h localhost -U scan2food_user -d scan2food_db
   ```

3. **Check permissions:**
   ```bash
   ls -la /var/www/scan2food/application/scan2food/media/backup_db/
   ```

4. **View detailed logs:**
   ```bash
   cat /var/log/scan2food/backup.log
   ```

### If cron job doesn't run:

1. **Check cron service status:**
   ```bash
   sudo systemctl status cron
   ```

2. **Restart cron service:**
   ```bash
   sudo systemctl restart cron
   ```

3. **Check system logs:**
   ```bash
   grep CRON /var/log/syslog
   ```

## Manual Backup

To create a backup manually at any time:
```bash
cd /var/www/scan2food/application/scan2food
python3 backupScript/automated_backup.py
```

## Restore from Backup

To restore a backup:
```bash
cd /var/www/scan2food/application/scan2food
python3 backupScript/db_restore.py
```

Or manually:
```bash
psql -h localhost -U scan2food_user -d scan2food_db < media/backup_db/app_backup_DD-MMM-YYYY.sql
```

## Modifying Backup Schedule

To change the backup time, edit the cron job:
```bash
crontab -e
```

Cron format: `minute hour day month weekday command`
- `0 4 * * *` = 4:00 AM daily
- `0 2 * * *` = 2:00 AM daily
- `0 */6 * * *` = Every 6 hours
- `0 0 * * 0` = Midnight every Sunday

## Changing Retention Period

Edit `automated_backup.py` and change:
```python
cleanup_old_backups(backup_dir, days_to_keep=30)  # Change 30 to desired days
```

## Security Notes

- Backups are stored in the media folder accessible via web interface
- Only users with "change_theatre" permission can access the backup page
- Ensure proper file permissions (755 for directories, 644 for files)
- Consider encrypting backups for sensitive data
- Regularly test backup restoration

## Support

For issues or questions, check:
1. Backup logs: `/var/log/scan2food/backup.log`
2. Django logs: `journalctl -u gunicorn -n 100`
3. System logs: `/var/log/syslog`
