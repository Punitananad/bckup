#!/usr/bin/env python3
"""
Check Superusers Script

This script checks all users in the database and shows which ones are superusers.
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, '/var/www/scan2food/application/scan2food')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theatreApp.settings')
django.setup()

from django.contrib.auth.models import User


def check_users():
    """Check all users and show superuser status"""
    
    print("\n" + "="*80)
    print("  USER DATABASE CHECK")
    print("="*80 + "\n")
    
    # Get all users
    all_users = User.objects.all().order_by('username')
    superusers = User.objects.filter(is_superuser=True)
    staff_users = User.objects.filter(is_staff=True)
    
    print(f"Total users in database: {all_users.count()}")
    print(f"Superusers: {superusers.count()}")
    print(f"Staff users: {staff_users.count()}")
    print(f"Regular users: {all_users.count() - staff_users.count()}")
    
    if all_users.count() == 0:
        print("\n❌ No users found in the database!")
        return
    
    print("\n" + "="*80)
    print("ALL USERS:")
    print("="*80 + "\n")
    
    print(f"{'#':<5} {'Username':<25} {'Email':<30} {'Superuser':<12} {'Staff':<10}")
    print("-" * 90)
    
    for idx, user in enumerate(all_users, 1):
        superuser_status = "✅ YES" if user.is_superuser else "❌ NO"
        staff_status = "✅ YES" if user.is_staff else "❌ NO"
        
        print(f"{idx:<5} {user.username:<25} {(user.email or 'N/A'):<30} {superuser_status:<12} {staff_status:<10}")
    
    print("\n" + "="*80)
    
    if superusers.count() > 0:
        print("\nSUPERUSERS ONLY:")
        print("="*80 + "\n")
        
        print(f"{'#':<5} {'Username':<25} {'Email':<30} {'Last Login':<20}")
        print("-" * 90)
        
        for idx, user in enumerate(superusers, 1):
            last_login = user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Never'
            print(f"{idx:<5} {user.username:<25} {(user.email or 'N/A'):<30} {last_login:<20}")
        
        print("\n" + "="*80)


if __name__ == "__main__":
    try:
        check_users()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
