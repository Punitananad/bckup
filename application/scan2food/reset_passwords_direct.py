#!/usr/bin/env python3
"""
Direct PostgreSQL Password Reset Script
Bypasses Django ORM and connects directly to PostgreSQL
"""

import os
import sys
import psycopg2
from django.contrib.auth.hashers import make_password

# Database connection parameters from .env
DB_NAME = 'scan2food_db'
DB_USER = 'scan2food_user'
DB_PASSWORD = 'scann2Food'
DB_HOST = '127.0.0.1'
DB_PORT = '5432'


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
        last_two = username[-2:]
        digit1 = int(last_two[0])
        digit2 = int(last_two[1])
        total = digit1 + digit2
        password = f"scan@{last_two}{total}"
    else:
        password = f"scan@{username}1"
    
    return password


def main():
    print("\n" + "="*80)
    print("  DIRECT DATABASE PASSWORD RESET TOOL")
    print("="*80 + "\n")
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        
        # Get all users
        cursor.execute("SELECT id, username, email, is_superuser, is_staff FROM auth_user ORDER BY username")
        users = cursor.fetchall()
        
        if not users:
            print("❌ No users found in the database!")
            return
        
        print(f"Found {len(users)} user(s):\n")
        
        # Display all users with their new passwords
        print(f"{'#':<5} {'Username':<20} {'Email':<30} {'New Password':<20} {'Type':<15} {'Role':<12}")
        print("-" * 105)
        
        user_data = []
        for idx, (user_id, username, email, is_superuser, is_staff) in enumerate(users, 1):
            new_password = generate_password(username)
            user_type = "Mobile Number" if is_mobile_number(username) else "Non-Mobile"
            role = "Superuser" if is_superuser else ("Staff" if is_staff else "Regular")
            
            print(f"{idx:<5} {username:<20} {(email or 'N/A'):<30} {new_password:<20} {user_type:<15} {role:<12}")
            user_data.append({
                'id': user_id,
                'username': username,
                'password': new_password,
                'type': user_type,
                'role': role
            })
        
        print("\n" + "="*80)
        
        # Ask for confirmation
        response = input("\n⚠️  Do you want to reset passwords for ALL these users? (yes/no): ").strip().lower()
        
        if response not in ['yes', 'y']:
            print("\n❌ Password reset cancelled.")
            cursor.close()
            conn.close()
            return
        
        # Reset passwords
        print("\n🔄 Resetting passwords...\n")
        
        success_count = 0
        for data in user_data:
            try:
                user_id = data['id']
                new_password = data['password']
                username = data['username']
                
                # Hash the password using Django's make_password
                hashed_password = make_password(new_password)
                
                # Update the password in database
                cursor.execute(
                    "UPDATE auth_user SET password = %s WHERE id = %s",
                    (hashed_password, user_id)
                )
                print(f"✅ {username}: Password updated successfully")
                success_count += 1
            except Exception as e:
                print(f"❌ {username}: Failed to update password - {e}")
        
        # Commit the changes
        conn.commit()
        
        print("\n" + "="*80)
        print(f"✅ Password reset complete! {success_count}/{len(user_data)} users updated.")
        print("="*80 + "\n")
        
        # Save credentials to file
        save_response = input("💾 Do you want to save credentials to a file? (yes/no): ").strip().lower()
        
        if save_response in ['yes', 'y']:
            filename = "user_credentials.txt"
            with open(filename, 'w') as f:
                f.write("="*80 + "\n")
                f.write("  ALL USER CREDENTIALS\n")
                f.write(f"  Generated on: {os.popen('date').read().strip()}\n")
                f.write("="*80 + "\n\n")
                
                for idx, data in enumerate(user_data, 1):
                    f.write(f"{idx}. Username: {data['username']}\n")
                    f.write(f"   Password: {data['password']}\n")
                    f.write(f"   Type: {data['type']}\n")
                    f.write(f"   Role: {data['role']}\n")
                    f.write("-" * 80 + "\n")
            
            print(f"\n✅ Credentials saved to: {filename}")
            print(f"⚠️  IMPORTANT: Keep this file secure and delete after noting passwords!")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")
        sys.exit(0)
