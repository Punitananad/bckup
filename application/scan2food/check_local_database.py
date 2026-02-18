"""
Check if local database has data from production
Run from: application/scan2food/
Command: python check_local_database.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theatreApp.settings')
django.setup()

from django.contrib.auth.models import User
from theatre.models import UserProfile, Theatre

print("=" * 60)
print("LOCAL DATABASE CHECK")
print("=" * 60)

# Check users
users = User.objects.all()
print(f"\nTotal Users: {users.count()}")
if users.count() > 0:
    print("\nFirst 5 users:")
    for user in users[:5]:
        print(f"  - {user.username} ({user.email})")
        try:
            profile = user.userprofile
            print(f"    Theatre: {profile.theatre.name if profile.theatre else 'None'}")
        except:
            print(f"    No UserProfile")

# Check theatres
theatres = Theatre.objects.all()
print(f"\nTotal Theatres: {theatres.count()}")
if theatres.count() > 0:
    print("\nFirst 5 theatres:")
    for theatre in theatres[:5]:
        print(f"  - {theatre.name}")

print("\n" + "=" * 60)
if users.count() == 0:
    print("⚠️  Database is EMPTY - you need to restore from backup")
    print("\nTo restore:")
    print("1. Download backup from server")
    print("2. Run: python download_latest_backup.py")
    print("3. Restore to local PostgreSQL")
else:
    print("✓ Database has data - you can use existing users")
print("=" * 60)
