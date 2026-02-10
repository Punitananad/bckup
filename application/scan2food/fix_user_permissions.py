import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theatreApp.settings')
django.setup()

from django.contrib.auth.models import User, Group, Permission
from theatre.models import UserProfile

# Get the user
username = '7988269870'
u = User.objects.get(username=username)

print(f"User: {u.username}")
print(f"Current groups: {[g.name for g in u.groups.all()]}")

# Check what groups exist
all_groups = Group.objects.all()
print(f"\nAvailable groups: {[g.name for g in all_groups]}")

# Get or create 'admin' group with all permissions
admin_group, created = Group.objects.get_or_create(name='admin')
if created:
    print(f"\nCreated 'admin' group")
    # Add all permissions to admin group
    permissions = Permission.objects.all()
    admin_group.permissions.set(permissions)
    print(f"Added {permissions.count()} permissions to admin group")
else:
    print(f"\n'admin' group already exists with {admin_group.permissions.count()} permissions")

# Add user to admin group
u.groups.add(admin_group)
print(f"\nAdded user '{username}' to 'admin' group")
print(f"User groups now: {[g.name for g in u.groups.all()]}")
