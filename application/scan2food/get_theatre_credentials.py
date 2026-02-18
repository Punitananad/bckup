"""
Get theatre user credentials
Run from: application/scan2food/
Command: python get_theatre_credentials.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theatreApp.settings')
django.setup()

from django.contrib.auth.models import User
from theatre.models import UserProfile, Theatre

print("=" * 60)
print("THEATRE USER CREDENTIALS")
print("=" * 60)

users = User.objects.all()

print("\nUsers with Theatre Access:")
print("-" * 60)

for user in users:
    try:
        profile = user.userprofile
        if profile.theatre:
            print(f"\nUsername: {user.username}")
            print(f"Phone: {user.username if user.username.isdigit() else 'N/A'}")
            print(f"Email: {user.email if user.email else 'Not set'}")
            print(f"Theatre: {profile.theatre.name}")
            print(f"Is Staff: {user.is_staff}")
            print(f"Is Superuser: {user.is_superuser}")
            
            # Show permissions
            if user.groups.exists():
                groups = ", ".join([g.name for g in user.groups.all()])
                print(f"Groups: {groups}")
            
            print("-" * 60)
    except:
        pass

print("\n" + "=" * 60)
print("PASSWORD RESET INSTRUCTIONS")
print("=" * 60)
print("\nTo reset password for any user, run:")
print("python reset_superuser_passwords.py")
print("\nOr login with:")
print("Username: punit")
print("Password: (use reset script to set new password)")
print("=" * 60)
