"""
Grant all permissions to a theatre user
Run from: application/scan2food/
Command: python grant_all_permissions.py <username>
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theatreApp.settings')
django.setup()

from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType

def grant_permissions(username):
    print("=" * 60)
    print(f"GRANTING PERMISSIONS TO: {username}")
    print("=" * 60)
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"❌ User '{username}' not found!")
        return
    
    print(f"\n✓ Found user: {user.username}")
    
    # Get all permissions related to theatre operations
    permission_codenames = [
        'view_order',
        'add_order',
        'change_order',
        'delete_order',
        'view_fooditem',
        'add_fooditem',
        'change_fooditem',
        'delete_fooditem',
        'view_theatre',
        'add_theatre',
        'change_theatre',
        'delete_theatre',
        'view_payment',
        'add_payment',
        'change_payment',
        'delete_payment',
    ]
    
    print("\nGranting permissions:")
    granted = 0
    for codename in permission_codenames:
        try:
            permission = Permission.objects.get(codename=codename)
            user.user_permissions.add(permission)
            print(f"  ✓ {codename}")
            granted += 1
        except Permission.DoesNotExist:
            print(f"  ⚠️  {codename} (not found)")
    
    user.save()
    
    print(f"\n✓ Granted {granted} permissions to {username}")
    print("\n" + "=" * 60)
    print("DONE - User now has full theatre access")
    print("=" * 60)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python grant_all_permissions.py <username>")
        print("\nExample: python grant_all_permissions.py 8708093774")
        sys.exit(1)
    
    username = sys.argv[1]
    grant_permissions(username)
