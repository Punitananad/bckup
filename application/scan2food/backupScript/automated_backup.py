#!/usr/bin/env python3
"""
Automated Database Backup Script for Scan2Food
Saves backups to media/backup_db folder with proper naming format
"""
import os
import subprocess
import datetime
import sys
from pathlib import Path

# Add parent directory to path to import Django settings
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Database config
DB_NAME = os.environ.get('DB_NAME', 'scan2food_db')
DB_USER = os.environ.get('DB_USER', 'scan2food_user')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'CHANGE_THIS')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')

def backup_postgres():
    """Create PostgreSQL backup and save to media/backup_db folder"""
    
    # Directory for storing backups (media/backup_db)
    backup_dir = os.path.join(BASE_DIR, 'media', 'backup_db')
    os.makedirs(backup_dir, exist_ok=True)

    # File with timestamp in format: app_backup_DD-MMM-YYYY.sql
    timestamp = datetime.datetime.now().strftime("%d-%b-%Y")
    backup_file = os.path.join(backup_dir, f"app_backup_{timestamp}.sql")

    # Set environment variable for password (avoids password prompt)
    env = os.environ.copy()
    env["PGPASSWORD"] = DB_PASSWORD

    try:
        print(f"🔄 Starting backup for database: {DB_NAME}")
        print(f"📁 Backup location: {backup_file}")
        
        with open(backup_file, "w") as f:
            subprocess.run(
                [
                    "pg_dump",
                    "-h", DB_HOST,
                    "-p", DB_PORT,
                    "-U", DB_USER,
                    DB_NAME,
                ],
                stdout=f,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
                env=env,
            )
        
        # Get file size
        file_size = os.path.getsize(backup_file) / (1024 * 1024)  # Convert to MB
        print(f"✅ Backup successful!")
        print(f"📊 File size: {file_size:.2f} MB")
        print(f"📅 Timestamp: {timestamp}")
        
        # Clean up old backups (keep last 30 days)
        cleanup_old_backups(backup_dir, days_to_keep=30)
        
    except subprocess.CalledProcessError as e:
        print("❌ Backup failed!")
        print(f"Error: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)

def cleanup_old_backups(backup_dir, days_to_keep=30):
    """Remove backups older than specified days"""
    try:
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_to_keep)
        deleted_count = 0
        
        for filename in os.listdir(backup_dir):
            if filename.startswith('app_backup_') and filename.endswith('.sql'):
                file_path = os.path.join(backup_dir, filename)
                file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if file_time < cutoff_date:
                    os.remove(file_path)
                    deleted_count += 1
                    print(f"🗑️  Deleted old backup: {filename}")
        
        if deleted_count > 0:
            print(f"✅ Cleaned up {deleted_count} old backup(s)")
        else:
            print(f"ℹ️  No old backups to clean up")
            
    except Exception as e:
        print(f"⚠️  Warning: Could not clean up old backups: {str(e)}")

if __name__ == "__main__":
    backup_postgres()
