import os
import subprocess
import datetime

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

def backup_postgres():
    # Directory for storing backups
    backup_dir = "./backups"
    os.makedirs(backup_dir, exist_ok=True)

    # File with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"{DB_NAME}_backup_{timestamp}.sql")

    # Set environment variable for password (avoids password prompt)
    env = os.environ.copy()
    env["PGPASSWORD"] = DB_PASSWORD

    try:
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
        print(f"✅ Backup successful! File saved at: {backup_file}")
    except subprocess.CalledProcessError as e:
        print("❌ Backup failed!")
        print(e.stderr)

if __name__ == "__main__":
    backup_postgres()
