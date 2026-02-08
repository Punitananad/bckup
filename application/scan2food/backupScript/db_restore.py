#     RUN THE COMMAND
 
# psql -U postgres
# ALTER USER guru CREATEDB;



import os
import subprocess
import glob

# Database config (from environment variables)
import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.environ.get('DB_NAME', 'scan2food_db')
DB_USER = os.environ.get('DB_USER', 'scan2food_user')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'CHANGE_THIS')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')

# OLD CREDENTIALS (COMPROMISED - DO NOT USE):
# DB_NAME = "app"
# DB_USER = "guru"
# DB_PASSWORD = "guru@2003"

# Backup folder
BACKUP_DIR = "./backups"

def get_latest_backup():
    files = glob.glob(os.path.join(BACKUP_DIR, "*.sql"))
    if not files:
        return None
    return max(files, key=os.path.getctime)  # latest by creation time

def restore_postgres():
    env = os.environ.copy()
    env["PGPASSWORD"] = DB_PASSWORD

    backup_file = get_latest_backup()
    if not backup_file:
        print("❌ No backup file found in backups folder!")
        return

    try:
        # Drop the database if it exists
        subprocess.run(
            ["dropdb", "-h", DB_HOST, "-p", DB_PORT, "-U", DB_USER, DB_NAME],
            stderr=subprocess.DEVNULL,  # ignore error if DB doesn't exist
            env=env,
        )

        # Create a new empty database
        subprocess.run(
            ["createdb", "-h", DB_HOST, "-p", DB_PORT, "-U", DB_USER, DB_NAME],
            check=True,
            env=env,
        )

        # Restore from the latest backup file
        with open(backup_file, "r") as f:
            subprocess.run(
                ["psql", "-h", DB_HOST, "-p", DB_PORT, "-U", DB_USER, DB_NAME],
                stdin=f,
                check=True,
                env=env,
            )
        print(f"✅ Database restored successfully from {backup_file}")
    except subprocess.CalledProcessError as e:
        print("❌ Restore failed!")
        print(e.stderr)

if __name__ == "__main__":
    restore_postgres()
