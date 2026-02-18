#!/usr/bin/env python3
"""
Download Latest Database Backup from Production Server
This script connects to the server and downloads the most recent backup
"""

import subprocess
import os
from datetime import datetime

# Configuration
SERVER = "root@165.22.219.111"
BACKUP_DIR = "/var/www/scan2food/application/scan2food/backupScript/backups"
LOCAL_DIR = r"C:\Users\punit\Downloads"

print("=" * 60)
print("DOWNLOAD LATEST DATABASE BACKUP")
print("=" * 60)
print()

# Step 1: Find the latest backup on server
print("Step 1: Finding latest backup on server...")
print(f"Server: {SERVER}")
print(f"Backup directory: {BACKUP_DIR}")
print()

try:
    # Get list of backup files sorted by modification time
    cmd = f'ssh {SERVER} "ls -t {BACKUP_DIR}/*.sql 2>/dev/null | head -n 1"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ Error: Could not connect to server or find backups")
        print(f"Error: {result.stderr}")
        input("Press Enter to exit...")
        exit(1)
    
    latest_backup = result.stdout.strip()
    
    if not latest_backup:
        print("❌ Error: No backup files found on server!")
        print(f"Please check if backups exist at: {BACKUP_DIR}")
        input("Press Enter to exit...")
        exit(1)
    
    backup_filename = os.path.basename(latest_backup)
    print(f"✓ Latest backup found: {backup_filename}")
    print()
    
    # Step 2: Download the backup
    print("Step 2: Downloading backup...")
    local_path = os.path.join(LOCAL_DIR, backup_filename)
    print(f"From: {latest_backup}")
    print(f"To: {local_path}")
    print()
    
    # Download using SCP
    cmd = f'scp {SERVER}:{latest_backup} "{local_path}"'
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode == 0:
        # Get file size
        file_size = os.path.getsize(local_path)
        file_size_mb = file_size / (1024 * 1024)
        
        print()
        print("=" * 60)
        print("SUCCESS!")
        print("=" * 60)
        print()
        print("✓ Backup downloaded successfully!")
        print(f"Location: {local_path}")
        print(f"Size: {file_size_mb:.2f} MB")
        print()
        print("You can now restore this backup locally using:")
        print(f"python fetch_and_restore_db.py")
        print()
    else:
        print()
        print("=" * 60)
        print("ERROR!")
        print("=" * 60)
        print()
        print("❌ Failed to download backup.")
        print()
        print("Please check:")
        print("1. SSH connection is working (try: ssh root@165.22.219.111)")
        print("2. Backup files exist on server")
        print("3. You have write permissions to Downloads folder")
        print()

except Exception as e:
    print(f"❌ Error: {str(e)}")
    print()

input("Press Enter to exit...")
