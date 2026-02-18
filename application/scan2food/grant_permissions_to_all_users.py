"""
Grant permissions to ALL theatre users in the database
Run from: application/scan2food/
Command: python grant_permissions_to_all_users.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theatreApp.settings')
django.setup()

from django.contrib.auth.models import User, Permission
from theatre.models import UserProfile

def grant_permissions_to_all():
    print("=" * 60)
    print("GRANTING PERMISSIONS TO ALL THEATRE USERS")
    print("=" * 60)
    
    # Get all users with theatre profiles
    users_with_theatre = User.objects.filter(userprofile__theatre__isnull=False)
    
    print(f"\nFound {users_with_theatre.count()} theatre users")
    
    # Get all permissions
    permission_codenames = [
        'view_order', 'add_order', 'change_order', 'delete_order',
        'view_fooditem', 'add_fooditem', 'change_fooditem', 'delete_fooditem',
        'view_theatre', 'add_theatre', 'change_theatre', 'delete_theatre',
        'view_payment', 'add_payment', 'change_payment', 'delete_payment',
        'view_userprofile', 'add_userprofile', 'change_userprofile', 'delete_userprofile',
    ]
    
    permissions = []
    for codename in permission_codenames:
        try:
            permission = Permission.objects.get(codename=codename)
            permissions.append(permission)
        except Permission.DoesNotExist:
            pass
    
    print(f"Granting {len(permissions)} permissions to each user...\n")
    
    # Grant permissions to each user
    updated = 0
    for user in users_with_theatre:
        try:
            theatre_name = user.userprofile.theatre.name
        except:
            theatre_name = "Unknown"
        
        print(f"Processing: {user.username} (Theatre: {theatre_name})")
        
        for permission in permissions:
            user.user_permissions.add(permission)
        
        user.save()
        updated += 1
    
    print(f"\n✓ Updated {updated} users")
    print("\n" + "=" * 60)
    print("DONE - All theatre users now have full permissions")
    print("=" * 60)

if __name__ == '__main__':
    grant_permissions_to_all()
