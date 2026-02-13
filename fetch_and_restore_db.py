"""
Database Fetch and Restore Script
Fetches database backup from remote server and restores it locally

Usage:
    python fetch_and_restore_db.py <backup_filename>
    
Example:
    python fetch_and_restore_db.py app_backup_13-Feb-2026.sql
"""

import os
import subprocess
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('application/scan2food/.env')

# Database configuration
DB_NAME = os.environ.get('DB_NAME', 'scan2food_db')
DB_USER = os.environ.get('DB_USER', 'scan2food_user')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'CHANGE_THIS')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')

# Remote server configuration
REMOTE_USER = "guru"
REMOTE_HOST = "scan2food.com"
REMOTE_BACKUP_PATH = "/home/guru/application/scan2food/media/backup_db"
LOCAL_DOWNLOAD_PATH = "application/scan2food/backupScript/backups"

def print_header(message):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {message}")
    print("="*60 + "\n")

def fetch_backup_from_server(backup_filename):
    """Fetch database backup from remote server using SCP"""
    print_header("STEP 1: Fetching Database Backup")
    
    # Ensure local backup directory exists
    os.makedirs(LOCAL_DOWNLOAD_PATH, exist_ok=True)
    
    # Construct remote and local paths
    remote_file = f"{REMOTE_USER}@{REMOTE_HOST}:{REMOTE_BACKUP_PATH}/{backup_filename}"
    local_file = os.path.join(LOCAL_DOWNLOAD_PATH, backup_filename)
    
    print(f"📥 Downloading from: {remote_file}")
    print(f"📁 Saving to: {local_file}")
    
    try:
        # Execute SCP command
        result = subprocess.run(
            ["scp", remote_file, local_file],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ Backup file downloaded successfully!")
        return local_file
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to download backup file!")
        print(f"Error: {e.stderr}")
        sys.exit(1)

def restore_database(backup_file):
    """Drop current database and restore from backup"""
    print_header("STEP 2: Restoring Database")
    
    # Set PostgreSQL password in environment
    env = os.environ.copy()
    env["PGPASSWORD"] = DB_PASSWORD
    
    print(f"🗄️  Database: {DB_NAME}")
    print(f"👤 User: {DB_USER}")
    print(f"🖥️  Host: {DB_HOST}:{DB_PORT}")
    
    try:
        # Step 1: Drop existing database
        print("\n🗑️  Dropping existing database...")
        subprocess.run(
            ["dropdb", "-h", DB_HOST, "-p", DB_PORT, "-U", DB_USER, DB_NAME],
            stderr=subprocess.DEVNULL,  # Ignore error if DB doesn't exist
            env=env,
        )
        print("✅ Database dropped")
        
        # Step 2: Create new empty database
        print("\n🆕 Creating new database...")
        subprocess.run(
            ["createdb", "-h", DB_HOST, "-p", DB_PORT, "-U", DB_USER, DB_NAME],
            check=True,
            env=env,
        )
        print("✅ Database created")
        
        # Step 3: Restore from backup
        print(f"\n📦 Restoring from backup: {backup_file}")
        with open(backup_file, "r", encoding="utf-8") as f:
            subprocess.run(
                ["psql", "-h", DB_HOST, "-p", DB_PORT, "-U", DB_USER, DB_NAME],
                stdin=f,
                check=True,
                env=env,
            )
        print("✅ Database restored successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Database restore failed!")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"Error: {e.stderr}")
        sys.exit(1)

def main():
    """Main execution function"""
    print_header("Database Fetch and Restore Tool")
    
    # Check if backup filename is provided
    if len(sys.argv) < 2:
        print("❌ Error: Backup filename not provided!")
        print("\nUsage:")
        print("  python fetch_and_restore_db.py <backup_filename>")
        print("\nExample:")
        print("  python fetch_and_restore_db.py app_backup_13-Feb-2026.sql")
        sys.exit(1)
    
    backup_filename = sys.argv[1]
    
    # Validate backup filename
    if not backup_filename.endswith('.sql'):
        print("⚠️  Warning: Backup file should have .sql extension")
    
    # Step 1: Fetch backup from server
    local_backup_file = fetch_backup_from_server(backup_filename)
    
    # Step 2: Restore database
    restore_database(local_backup_file)
    
    # Success message
    print_header("✅ COMPLETE!")
    print("Database has been successfully fetched and restored.")
    print(f"Backup file saved at: {local_backup_file}")
    print("\n💡 Next steps:")
    print("  1. Restart your Django application")
    print("  2. Run migrations if needed: python manage.py migrate")
    print("  3. Test the application\n")

if __name__ == "__main__":
    main()

