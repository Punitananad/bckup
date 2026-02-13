#!/usr/bin/env python3
"""
Reset Superuser Passwords Script

This script lists all superusers and resets their passwords based on a pattern:
- If username is a 10-digit mobile number: scan@{last2digits}{sum}
  Example: 7988269874 -> scan@7411 (74 are last 2 digits, 11 is 7+4)
- If username is NOT a mobile number: scan@{username}1

Usage:
    python reset_superuser_passwords.py
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, '/var/www/scan2food/application/scan2food')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theatreApp.settings')
django.setup()

from django.contrib.auth.models import User


def is_mobile_number(username):
    """Check if username is a 10-digit mobile number"""
    return username.isdigit() and len(username) == 10


def generate_password(username):
    """
    Generate password based on username pattern:
    - Mobile number (10 digits): scan@{last2digits}{sum}
    - Non-mobile: scan@{username}1
    """
    if is_mobile_number(username):
        # Get last 2 digits
        last_two = username[-2:]
        digit1 = int(last_two[0])
        digit2 = int(last_two[1])
        total = digit1 + digit2
        password = f"scan@{last_two}{total}"
    else:
        # Non-mobile username
        password = f"scan@{username}1"
    
    return password


def list_and_reset_superusers():
    """List all superusers and reset their passwords"""
    
    print("\n" + "="*80)
    print("  SUPERUSER PASSWORD RESET TOOL")
    print("="*80 + "\n")
    
    # Get all superusers
    superusers = User.objects.filter(is_superuser=True).order_by('username')
    
    if not superusers.exists():
        print("❌ No superusers found in the database!")
        return
    
    print(f"Found {superusers.count()} superuser(s):\n")
    
    # Display all superusers with their new passwords
    print(f"{'#':<5} {'Username':<20} {'Email':<30} {'New Password':<20} {'Type':<15}")
    print("-" * 90)
    
    user_data = []
    for idx, user in enumerate(superusers, 1):
        new_password = generate_password(user.username)
        user_type = "Mobile Number" if is_mobile_number(user.username) else "Non-Mobile"
        
        print(f"{idx:<5} {user.username:<20} {user.email or 'N/A':<30} {new_password:<20} {user_type:<15}")
        user_data.append({
            'user': user,
            'password': new_password,
            'type': user_type
        })
    
    print("\n" + "="*80)
    
    # Ask for confirmation
    response = input("\n⚠️  Do you want to reset passwords for ALL these superusers? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("\n❌ Password reset cancelled.")
        return
    
    # Reset passwords
    print("\n🔄 Resetting passwords...\n")
    
    success_count = 0
    for data in user_data:
        try:
            user = data['user']
            new_password = data['password']
            user.set_password(new_password)
            user.save()
            print(f"✅ {user.username}: Password updated successfully")
            success_count += 1
        except Exception as e:
            print(f"❌ {user.username}: Failed to update password - {e}")
    
    print("\n" + "="*80)
    print(f"✅ Password reset complete! {success_count}/{len(user_data)} users updated.")
    print("="*80 + "\n")
    
    # Save credentials to file
    save_response = input("💾 Do you want to save credentials to a file? (yes/no): ").strip().lower()
    
    if save_response in ['yes', 'y']:
        filename = "superuser_credentials.txt"
        with open(filename, 'w') as f:
            f.write("="*80 + "\n")
            f.write("  SUPERUSER CREDENTIALS\n")
            f.write(f"  Generated on: {django.utils.timezone.now()}\n")
            f.write("="*80 + "\n\n")
            
            for idx, data in enumerate(user_data, 1):
                f.write(f"{idx}. Username: {data['user'].username}\n")
                f.write(f"   Password: {data['password']}\n")
                f.write(f"   Email: {data['user'].email or 'N/A'}\n")
                f.write(f"   Type: {data['type']}\n")
                f.write("-" * 80 + "\n")
        
        print(f"\n✅ Credentials saved to: {filename}")


if __name__ == "__main__":
    try:
        list_and_reset_superusers()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
