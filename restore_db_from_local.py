#!/usr/bin/env python3
"""
Database Restore Script (Server-Side Version)
Restores database from a local backup file on the server

Usage:
    python3 restore_db_from_local.py <backup_filename>
    
Example:
    python3 restore_db_from_local.py app_backup_13-Feb-2026.sql
"""

import os
import subprocess
import sys
from pathlib import Path

# Try to load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv('/var/www/scan2food/application/scan2food/.env')
except ImportError:
    print("⚠️  python-dotenv not installed, using environment variables only")

# Database configuration
DB_NAME = os.environ.get('DB_NAME', 'scan2food_db')
DB_USER = os.environ.get('DB_USER', 'scan2food_user')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'CHANGE_THIS')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')

# Backup locations to search
BACKUP_LOCATIONS = [
    "/home/guru/application/scan2food/media/backup_db",
    "/var/www/scan2food/application/scan2food/backupScript/backups",
    "./application/scan2food/backupScript/backups",
    "./backups"
]

def print_header(message):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {message}")
    print("="*60 + "\n")

def find_backup_file(backup_filename):
    """Find backup file in common locations"""
    print_header("Searching for Backup File")
    
    # If full path provided, use it directly
    if os.path.isfile(backup_filename):
        print(f"✅ Found: {backup_filename}")
        return backup_filename
    
    # Search in common locations
    for location in BACKUP_LOCATIONS:
        backup_path = os.path.join(location, backup_filename)
        print(f"🔍 Checking: {backup_path}")
        if os.path.isfile(backup_path):
            print(f"✅ Found: {backup_path}")
            return backup_path
    
    print(f"❌ Backup file not found: {backup_filename}")
    print("\nSearched in:")
    for location in BACKUP_LOCATIONS:
        print(f"  - {location}")
    return None

def restore_database(backup_file):
    """Drop current database and restore from backup"""
    print_header("Restoring Database")
    
    # Set PostgreSQL password in environment
    env = os.environ.copy()
    env["PGPASSWORD"] = DB_PASSWORD
    
    print(f"🗄️  Database: {DB_NAME}")
    print(f"👤 User: {DB_USER}")
    print(f"🖥️  Host: {DB_HOST}:{DB_PORT}")
    print(f"📦 Backup: {backup_file}")
    
    try:
        # Step 1: Drop existing database
        print("\n🗑️  Dropping existing database...")
        result = subprocess.run(
            ["dropdb", "-h", DB_HOST, "-p", DB_PORT, "-U", DB_USER, DB_NAME],
            stderr=subprocess.PIPE,
            env=env,
        )
        if result.returncode == 0:
            print("✅ Database dropped")
        else:
            print("⚠️  Database may not exist (this is OK)")
        
        # Step 2: Create new empty database
        print("\n🆕 Creating new database...")
        subprocess.run(
            ["createdb", "-h", DB_HOST, "-p", DB_PORT, "-U", DB_USER, DB_NAME],
            check=True,
            env=env,
            stderr=subprocess.PIPE,
        )
        print("✅ Database created")
        
        # Step 3: Restore from backup
        print(f"\n📦 Restoring from backup...")
        print("⏳ This may take a few minutes...")
        
        with open(backup_file, "r", encoding="utf-8") as f:
            result = subprocess.run(
                ["psql", "-h", DB_HOST, "-p", DB_PORT, "-U", DB_USER, DB_NAME],
                stdin=f,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
            )
        
        if result.returncode == 0:
            print("✅ Database restored successfully!")
        else:
            print("⚠️  Restore completed with warnings")
            if result.stderr:
                stderr_text = result.stderr.decode('utf-8', errors='ignore')
                # Only show first few lines of errors
                error_lines = stderr_text.split('\n')[:10]
                print("\nWarnings/Errors:")
                for line in error_lines:
                    if line.strip():
                        print(f"  {line}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Database restore failed!")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"Error: {e.stderr.decode('utf-8', errors='ignore')}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

def main():
    """Main execution function"""
    print_header("Database Restore Tool (Server-Side)")
    
    # Check if backup filename is provided
    if len(sys.argv) < 2:
        print("❌ Error: Backup filename not provided!")
        print("\nUsage:")
        print("  python3 restore_db_from_local.py <backup_filename>")
        print("\nExample:")
        print("  python3 restore_db_from_local.py app_backup_13-Feb-2026.sql")
        print("\nOr provide full path:")
        print("  python3 restore_db_from_local.py /home/guru/application/scan2food/media/backup_db/app_backup_13-Feb-2026.sql")
        sys.exit(1)
    
    backup_filename = sys.argv[1]
    
    # Find backup file
    backup_file = find_backup_file(backup_filename)
    if not backup_file:
        sys.exit(1)
    
    # Confirm before proceeding
    print("\n⚠️  WARNING: This will DROP the current database and restore from backup!")
    print(f"Database: {DB_NAME}")
    print(f"Backup: {backup_file}")
    
    response = input("\nDo you want to continue? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print("❌ Restore cancelled by user")
        sys.exit(0)
    
    # Restore database
    restore_database(backup_file)
    
    # Success message
    print_header("✅ COMPLETE!")
    print("Database has been successfully restored.")
    print("\n💡 Next steps:")
    print("  1. Restart Django services:")
    print("     sudo systemctl restart gunicorn")
    print("     sudo systemctl restart daphne")
    print("  2. Check application logs:")
    print("     sudo journalctl -u gunicorn -f")
    print("  3. Test the application\n")

if __name__ == "__main__":
    main()
