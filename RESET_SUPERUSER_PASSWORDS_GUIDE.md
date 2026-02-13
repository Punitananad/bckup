# Reset User Passwords Guide

## What This Script Does

This script will:
1. List ALL users in the database (superusers, staff, and regular users)
2. Show their current usernames, emails, and roles
3. Generate new passwords based on a pattern
4. Reset all user passwords
5. Optionally save credentials to a file

## Password Pattern

### For Mobile Number Usernames (10 digits):
- Pattern: `scan@{last2digits}{sum}`
- Example: Username `7988269874` → Password `scan@7411`
  - Last 2 digits: 74
  - Sum: 7 + 4 = 11
  - Password: scan@7411

### For Non-Mobile Usernames:
- Pattern: `scan@{username}1`
- Example: Username `admin` → Password `scan@admin1`

## How to Use

### Step 1: SSH into the Server
```bash
ssh root@165.22.219.111
cd /var/www/scan2food
```

### Step 2: Run the Script
```bash
python3 application/scan2food/reset_superuser_passwords.py
```

### Step 3: Review the List
The script will show you all users with their new passwords and roles (Superuser/Staff/Regular).

### Step 4: Confirm
Type `yes` to reset passwords, or `no` to cancel.

### Step 5: Save Credentials (Optional)
The script will ask if you want to save credentials to a file.
- Type `yes` to save to `user_credentials.txt`
- Type `no` to skip

## Example Output

```
================================================================================
  USER PASSWORD RESET TOOL
================================================================================

Found 35 user(s):

#     Username             Email                          New Password         Type            Role        
---------------------------------------------------------------------------------------------------------
1     7988269874           user1@example.com              scan@7411            Mobile Number   Superuser   
2     9876543210           user2@example.com              scan@1011            Mobile Number   Staff       
3     admin                admin@example.com              scan@admin1          Non-Mobile      Superuser   
4     8765432109           user3@example.com              scan@0910            Mobile Number   Regular     
...

================================================================================

⚠️  Do you want to reset passwords for ALL these users? (yes/no): yes

🔄 Resetting passwords...

✅ 7988269874: Password updated successfully
✅ 9876543210: Password updated successfully
✅ admin: Password updated successfully
✅ 8765432109: Password updated successfully
...

================================================================================
✅ Password reset complete! 35/35 users updated.
================================================================================
```

## Important Notes

- ⚠️ This will change passwords for ALL users in the database
- Make sure to save the credentials file if you need them later
- The credentials file will be saved in `/var/www/scan2food/user_credentials.txt`
- Keep the credentials file secure and delete it after noting down the passwords

## Troubleshooting

### If you get "Module not found" error:
Make sure you're in the correct directory:
```bash
cd /var/www/scan2food
```

### If Django settings error:
Make sure the `.env` file exists:
```bash
ls -la application/scan2food/.env
```

## Security

After running this script:
1. Note down all the new passwords
2. Delete the credentials file: `rm user_credentials.txt`
3. Store passwords securely (password manager)
