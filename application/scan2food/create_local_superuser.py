"""
Create a superuser for local development
Run this from: application/scan2food/
Command: python create_local_superuser.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theatreApp.settings')
django.setup()

from django.contrib.auth.models import User, Group, Permission
from theatre.models import UserProfile, Theatre

def create_superuser():
    print("=" * 60)
    print("CREATE LOCAL SUPERUSER")
    print("=" * 60)
    
    # Check if superuser already exists
    username = "admin"
    if User.objects.filter(username=username).exists():
        print(f"✓ Superuser '{username}' already exists")
        user = User.objects.get(username=username)
        print(f"  Email: {user.email}")
        print(f"  Is superuser: {user.is_superuser}")
        print(f"  Is staff: {user.is_staff}")
        return
    
    # Create superuser
    print(f"\nCreating superuser '{username}'...")
    user = User.objects.create_superuser(
        username=username,
        email='admin@scan2food.com',
        password='admin123',  # Change this after first login!
        first_name='Admin',
        last_name='User'
    )
    
    # Make sure user is staff and superuser
    user.is_staff = True
    user.is_superuser = True
    user.save()
    
    print(f"✓ Superuser created successfully!")
    print(f"\n  Username: {username}")
    print(f"  Password: admin123")
    print(f"  Email: {user.email}")
    print(f"\n⚠️  IMPORTANT: Change the password after first login!")
    
    # Add to admin group if it exists
    try:
        admin_group = Group.objects.get(name='admin')
        user.groups.add(admin_group)
        print(f"✓ Added to 'admin' group")
    except Group.DoesNotExist:
        print(f"⚠️  'admin' group doesn't exist yet")
    
    print("\n" + "=" * 60)
    print("LOGIN INSTRUCTIONS")
    print("=" * 60)
    print("1. Go to: http://localhost:8000/admin/")
    print("2. Login with:")
    print("   Username: admin")
    print("   Password: admin123")
    print("3. After login, you can access all theatre pages")
    print("=" * 60)

if __name__ == '__main__':
    create_superuser()
