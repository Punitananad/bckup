import os
import subprocess
import datetime
from dotenv import load_dotenv

load_dotenv()

# Database config
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
BACKUP_DIR = os.getenv("BACKUP_DIR")

MAX_BACKUPS = 30   # how many backups you want to keep


def get_oldest_backup_file(directory):
    files = [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f))
    ]

    if len(files) < MAX_BACKUPS:
        return None

    # sort by last modified time (oldest first)
    files.sort(key=os.path.getmtime)
    return files[0]   # oldest file


def backup_postgres():
    os.makedirs(BACKUP_DIR, exist_ok=True)

    # Find oldest backup BEFORE creating new one
    oldest_backup = get_oldest_backup_file(BACKUP_DIR)

    timestamp = datetime.datetime.now().strftime("%d-%b-%Y")
    backup_file = os.path.join(
        BACKUP_DIR, f"{DB_NAME}_backup_{timestamp}.sql"
    )

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

        print(f"✅ Backup successful: {backup_file}")

        # Delete ONLY the oldest file
        if oldest_backup:
            os.remove(oldest_backup)
            print(f"🗑️ Deleted oldest backup: {oldest_backup}")

    except subprocess.CalledProcessError as e:
        print("❌ Backup failed!")
        print(e.stderr)
        # No deletion if backup fails


if __name__ == "__main__":
    backup_postgres()
