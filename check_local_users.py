import os
import sys
import django

# Add the application directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'application', 'scan2food'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theatreApp.settings')
django.setup()

from django.contrib.auth.models import User, Group
from theatre.models import UserProfile, Theatre

print("=" * 60)
print("CHECKING LOCAL DATABASE USERS")
print("=" * 60)

# Check all users
users = User.objects.all()
print(f"\nTotal users in database: {users.count()}")

if users.count() == 0:
    print("\nNo users found! Creating a test theatre owner...")
    
    # Check if theatre exists
    theatre = Theatre.objects.first()
    if not theatre:
        print("ERROR: No theatre found in database!")
        print("Please create a theatre first or restore the database.")
        sys.exit(1)
    
    # Create theatre owner group if it doesn't exist
    theatre_owner_group, created = Group.objects.get_or_create(name='theatre_owner')
    
    # Create test user
    test_user = User.objects.create_user(
        username='testowner',
        password='test123',
        email='test@example.com',
        first_name='Test',
        last_name='Owner'
    )
    test_user.groups.add(theatre_owner_group)
    test_user.save()
    
    # Create user profile
    profile = UserProfile.objects.create(
        user=test_user,
        theatre=theatre,
        active_status=True
    )
    
    print(f"\n✓ Created test user:")
    print(f"  Username: testowner")
    print(f"  Password: test123")
    print(f"  Theatre: {theatre.name}")
    print(f"\nYou can now login at: http://localhost:8000/login")
else:
    print("\nExisting users:")
    for user in users:
        print(f"\n  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Is superuser: {user.is_superuser}")
        print(f"  Groups: {', '.join([g.name for g in user.groups.all()]) or 'None'}")
        
        try:
            profile = user.userprofile
            print(f"  Theatre: {profile.theatre.name if profile.theatre else 'None'}")
            print(f"  Active: {profile.active_status}")
        except:
            print(f"  Profile: No UserProfile")

print("\n" + "=" * 60)
print("LOGIN INSTRUCTIONS")
print("=" * 60)
print("\n1. Go to: http://localhost:8000/login")
print("2. Use one of the usernames above")
print("3. If you don't know the password, you can reset it using Django admin")
print("\nFor superusers, you can also access Django admin at:")
print("http://localhost:8000/admin")
print("=" * 60)
