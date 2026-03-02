#!/bin/bash
# Setup automated database backup cron job for Scan2Food
# This script configures a cron job to run daily at 4:00 AM

echo "=== Scan2Food Automated Backup Setup ==="
echo ""

# Define paths
PROJECT_DIR="/var/www/scan2food/application/scan2food"
BACKUP_SCRIPT="$PROJECT_DIR/backupScript/automated_backup.py"
LOG_DIR="/var/log/scan2food"
LOG_FILE="$LOG_DIR/backup.log"

# Create log directory
echo "📁 Creating log directory..."
mkdir -p "$LOG_DIR"
chown www-data:www-data "$LOG_DIR"
chmod 755 "$LOG_DIR"

# Make backup script executable
echo "🔧 Making backup script executable..."
chmod +x "$BACKUP_SCRIPT"

# Create cron job
CRON_JOB="0 4 * * * cd $PROJECT_DIR && /usr/bin/python3 $BACKUP_SCRIPT >> $LOG_FILE 2>&1"

echo ""
echo "📋 Cron job to be added:"
echo "$CRON_JOB"
echo ""

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "automated_backup.py"; then
    echo "⚠️  Cron job already exists. Removing old entry..."
    crontab -l 2>/dev/null | grep -v "automated_backup.py" | crontab -
fi

# Add new cron job
echo "➕ Adding cron job..."
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo ""
echo "✅ Cron job added successfully!"
echo ""
echo "📅 Backup Schedule:"
echo "   - Time: 4:00 AM daily"
echo "   - Location: $PROJECT_DIR/media/backup_db/"
echo "   - Log file: $LOG_FILE"
echo "   - Retention: 30 days"
echo ""
echo "🔍 To verify the cron job:"
echo "   crontab -l"
echo ""
echo "📊 To view backup logs:"
echo "   tail -f $LOG_FILE"
echo ""
echo "🧪 To test the backup manually:"
echo "   cd $PROJECT_DIR && python3 $BACKUP_SCRIPT"
echo ""

# Test the backup script
echo "🧪 Running test backup..."
cd "$PROJECT_DIR" && python3 "$BACKUP_SCRIPT"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Test backup successful!"
    echo "🎉 Automated backup system is ready!"
else
    echo ""
    echo "❌ Test backup failed. Please check the configuration."
    exit 1
fi
