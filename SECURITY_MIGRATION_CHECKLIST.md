# 🚨 CRITICAL SECURITY MIGRATION CHECKLIST
## Protecting scan2food.com from Previous Developer

---

## ⚠️ SITUATION SUMMARY
- **Current Status:** Live site at scan2food.com (old server)
- **Risk:** Previous developer has access and may sabotage
- **Action:** Migrate to new IP with ALL security credentials changed
- **Priority:** CRITICAL - Do this IMMEDIATELY

---

## 🔐 STEP 1: CHANGE ALL SECURITY KEYS (HIGHEST PRIORITY)

### 1.1 Django SECRET_KEY
**Location:** `application/scan2food/theatreApp/settings.py` line 21

**Current Key (COMPROMISED):**
```
django-insecure-a@q^h)$szzhw_$wd)0zu@8x^woi^d9vufw#^!-uuhv2%j2r%*e
```

**Action:**
- Generate NEW secret key
- Replace in settings.py
- This invalidates all old sessions/cookies

**How to Generate:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 💳 STEP 2: CHANGE ALL PAYMENT GATEWAY CREDENTIALS

### 2.1 Razorpay (if used)
**Where stored:** Database table `adminPortal_paymentgateway`

**What to change:**
- ✅ Create NEW Razorpay account OR
- ✅ Generate NEW API Key ID and Secret from Razorpay dashboard
- ✅ Revoke OLD keys immediately

**Razorpay Dashboard:**
- Login: https://dashboard.razorpay.com/
- Go to: Settings → API Keys
- Generate Test/Live Keys
- **IMMEDIATELY REVOKE old keys**

**Critical:** Old developer can:
- ❌ Process refunds to himself
- ❌ See all transactions
- ❌ Modify payment amounts
- ❌ Access customer payment data

---

### 2.2 Cashfree (if used)
**Where stored:** Database table `adminPortal_paymentgateway`

**What to change:**
- ✅ Generate NEW App ID and Secret Key
- ✅ Revoke OLD credentials

**Cashfree Dashboard:**
- Login: https://merchant.cashfree.com/
- Go to: Developers → Credentials
- Generate new credentials
- **IMMEDIATELY REVOKE old credentials**

---

### 2.3 PhonePe (if used)
**Where stored:** Database table `adminPortal_paymentgateway`

**What to change:**
- ✅ Generate NEW Merchant ID and Salt Key
- ✅ Revoke OLD credentials

**PhonePe Dashboard:**
- Contact PhonePe support to revoke old credentials
- Generate new merchant credentials

---

### 2.4 PayU (if used)
**Where stored:** Database table `adminPortal_paymentgateway`

**What to change:**
- ✅ Generate NEW Merchant Key and Salt
- ✅ Revoke OLD credentials

---

### 2.5 CCAvenue (if used)
**Where stored:** Database table `adminPortal_paymentgateway`

**What to change:**
- ✅ Generate NEW Merchant ID and Working Key
- ✅ Revoke OLD credentials

---

## 🗄️ STEP 3: DATABASE SECURITY

### 3.1 Change Database Credentials
**If using PostgreSQL (production):**

**Current credentials in settings.py (commented):**
```
USER: 'guru'
PASSWORD: 'guru@2003'
```

**Action:**
- ✅ Create NEW database user
- ✅ Create NEW strong password
- ✅ Grant permissions to new user
- ✅ Update settings.py with new credentials
- ✅ DROP old user 'guru' from database

**PostgreSQL Commands:**
```sql
-- Create new user
CREATE USER scan2food_new WITH PASSWORD 'your_new_strong_password_here';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE app TO scan2food_new;

-- After migration, drop old user
DROP USER guru;
```

---

### 3.2 Backup Current Database
**BEFORE making any changes:**

```bash
# If SQLite (current)
cp application/scan2food/db.sqlite3 db_backup_$(date +%Y%m%d).sqlite3

# If PostgreSQL
pg_dump -U guru -d app > backup_before_migration.sql
```

---

## 👤 STEP 4: CHANGE ALL ADMIN ACCOUNTS

### 4.1 Django Superuser
**Current admin found:**
- Username: `punit`
- Email: `punitanand146@gmail.com`

**Action:**
- ✅ Change password for 'punit' account
- ✅ Check for OTHER admin accounts created by old developer
- ✅ Delete any suspicious admin accounts
- ✅ Create NEW superuser with different username

**Commands:**
```bash
# Change password
python manage.py changepassword punit

# List all superusers
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.filter(is_superuser=True)

# Delete suspicious users
>>> User.objects.filter(username='old_dev_username').delete()

# Create new superuser
python manage.py createsuperuser
```

---

### 4.2 Restaurant/Theatre Owner Accounts
**Check in database:**
- Table: `auth_user`
- Table: `adminPortal_detail`

**Action:**
- ✅ Review all user accounts
- ✅ Delete accounts created by old developer
- ✅ Change passwords for owner accounts

---

## 🔌 STEP 5: REDIS SECURITY

### 5.1 Redis Password
**Current:** No password (default)

**Action:**
- ✅ Set Redis password
- ✅ Update settings.py with Redis password

**Redis Configuration:**
```bash
# Edit redis.conf
sudo nano /etc/redis/redis.conf

# Add/uncomment:
requirepass your_strong_redis_password_here

# Restart Redis
sudo systemctl restart redis
```

**Update settings.py:**
```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
            "password": "your_strong_redis_password_here",
        },
    },
}
```

---

## 🌐 STEP 6: SERVER ACCESS SECURITY

### 6.1 Change Server Passwords
- ✅ Change SSH password
- ✅ Change root password
- ✅ Disable old developer's SSH keys

**Commands:**
```bash
# Change user password
passwd

# Change root password
sudo passwd root

# Remove old SSH keys
nano ~/.ssh/authorized_keys
# Delete old developer's public key

# Disable password authentication (use keys only)
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
sudo systemctl restart sshd
```

---

### 6.2 Firewall Rules
- ✅ Update firewall to block old server IP
- ✅ Allow only necessary ports

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

---

## 📧 STEP 7: EMAIL & NOTIFICATION CREDENTIALS

### 7.1 Email Settings
**If configured in settings.py or database:**

**Action:**
- ✅ Change email account password
- ✅ Generate NEW app-specific password (Gmail)
- ✅ Revoke old app passwords

---

### 7.2 Firebase/Push Notifications
**If using Firebase:**

**Action:**
- ✅ Generate NEW Firebase service account key
- ✅ Delete OLD service account
- ✅ Update credentials file

**Firebase Console:**
- Go to: Project Settings → Service Accounts
- Generate new private key
- Delete old service account

---

## 🔗 STEP 8: WEBHOOK URLS & CALLBACKS

### 8.1 Update Payment Gateway Webhooks
**All payment gateways have webhook URLs pointing to old server**

**Action:**
- ✅ Update Razorpay webhook URL to new IP
- ✅ Update Cashfree webhook URL to new IP
- ✅ Update PhonePe webhook URL to new IP
- ✅ Update PayU webhook URL to new IP

**Example URLs to update:**
```
OLD: https://scan2food.com/theatre/api/razorpay-webhook-url
NEW: https://NEW_IP/theatre/api/razorpay-webhook-url
```

---

## 🚫 STEP 9: REVOKE OLD SERVER ACCESS

### 9.1 Domain DNS
**Action:**
- ✅ Update DNS A record to point to NEW IP
- ✅ Wait for DNS propagation (24-48 hours)
- ✅ Keep old server running during transition

**DNS Changes:**
```
OLD: scan2food.com → 134.209.149.31
NEW: scan2food.com → YOUR_NEW_IP
```

---

### 9.2 SSL Certificate
**Action:**
- ✅ Generate NEW SSL certificate on new server
- ✅ Use Let's Encrypt (free)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d scan2food.com -d www.scan2food.com
```

---

## 📱 STEP 10: THIRD-PARTY INTEGRATIONS

### 10.1 WhatsApp Business API (if used)
**Action:**
- ✅ Update webhook URLs
- ✅ Regenerate access tokens

---

### 10.2 SMS Gateway (if used)
**Action:**
- ✅ Change API credentials
- ✅ Update sender IDs if needed

---

## 🔍 STEP 11: CODE REVIEW FOR BACKDOORS

### 11.1 Check for Malicious Code
**Search for:**
- Hidden admin accounts
- Backdoor URLs
- Remote code execution
- Data exfiltration code

**Files to review carefully:**
```
application/scan2food/theatreApp/urls.py
application/scan2food/theatre/views.py
application/scan2food/adminPortal/views.py
application/scan2food/theatre/api_views.py
```

**Search for suspicious patterns:**
```bash
# Search for eval/exec (code execution)
grep -r "eval(" application/scan2food/
grep -r "exec(" application/scan2food/

# Search for suspicious URLs
grep -r "http://" application/scan2food/ | grep -v "localhost"

# Search for hardcoded IPs
grep -r "[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}" application/scan2food/
```

---

## 📋 STEP 12: SETTINGS.PY SECURITY UPDATES

### 12.1 Update settings.py
**File:** `application/scan2food/theatreApp/settings.py`

**Changes needed:**
```python
# Line 21: NEW SECRET_KEY
SECRET_KEY = 'your-new-generated-secret-key-here'

# Line 24: Set to False
DEBUG = False

# Line 26: Update with NEW IP
ALLOWED_HOSTS = ['YOUR_NEW_IP', 'scan2food.com', 'www.scan2food.com']

# Add CSRF trusted origins
CSRF_TRUSTED_ORIGINS = [
    'https://scan2food.com',
    'https://www.scan2food.com',
]

# Add security headers
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

---

## ✅ MIGRATION EXECUTION ORDER

### Phase 1: Preparation (Do First)
1. ✅ Backup current database from live server
2. ✅ Copy all media files from live server
3. ✅ Document current payment gateway credentials
4. ✅ Set up new server with fresh installation

### Phase 2: Security Changes (Critical)
5. ✅ Generate NEW Django SECRET_KEY
6. ✅ Generate NEW payment gateway credentials
7. ✅ Change all database passwords
8. ✅ Change all admin account passwords
9. ✅ Set Redis password

### Phase 3: Deployment
10. ✅ Deploy code to new server
11. ✅ Restore database backup
12. ✅ Update payment gateway credentials in database
13. ✅ Update webhook URLs in payment gateways
14. ✅ Test all payment flows

### Phase 4: Go Live
15. ✅ Update DNS to point to new IP
16. ✅ Generate SSL certificate
17. ✅ Monitor for 24-48 hours
18. ✅ Revoke ALL old credentials

### Phase 5: Cleanup
19. ✅ Delete old developer's access
20. ✅ Shut down old server
21. ✅ Document new credentials securely

---

## 🚨 IMMEDIATE ACTIONS (DO NOW)

### Priority 1 (Within 1 hour):
1. **Backup database from live server**
2. **Change Django admin password**
3. **Generate new payment gateway credentials**

### Priority 2 (Within 24 hours):
4. **Deploy to new server**
5. **Update DNS**
6. **Revoke old payment gateway keys**

### Priority 3 (Within 48 hours):
7. **Monitor all transactions**
8. **Verify no unauthorized access**
9. **Shut down old server**

---

## 📞 EMERGENCY CONTACTS

### If Old Developer Causes Damage:
1. **Immediately revoke payment gateway credentials**
2. **Contact payment gateway support**
3. **Take old server offline**
4. **Restore from backup**

### Payment Gateway Support:
- **Razorpay:** support@razorpay.com | 1800-102-0480
- **Cashfree:** care@cashfree.com | 080-68727374
- **PhonePe:** merchantsupport@phonepe.com

---

## 🔒 CREDENTIALS STORAGE

### DO NOT store credentials in:
- ❌ Code repository (GitHub, GitLab)
- ❌ Shared documents
- ❌ Email
- ❌ Slack/WhatsApp

### DO store credentials in:
- ✅ Password manager (1Password, LastPass, Bitwarden)
- ✅ Encrypted file on secure server
- ✅ Environment variables on server only

---

## 📝 CHECKLIST SUMMARY

```
[ ] Django SECRET_KEY changed
[ ] All payment gateway credentials changed
[ ] Database password changed
[ ] Admin passwords changed
[ ] Redis password set
[ ] SSH access secured
[ ] Webhook URLs updated
[ ] DNS updated to new IP
[ ] SSL certificate installed
[ ] Old credentials revoked
[ ] Code reviewed for backdoors
[ ] Backup created
[ ] New server tested
[ ] Old server shut down
```

---

## ⚠️ CRITICAL WARNING

**DO NOT:**
- Share this checklist with old developer
- Give old developer any access to new server
- Reuse any credentials from old server
- Trust any code changes made by old developer recently

**The old developer can:**
- Access payment gateway accounts
- Modify/delete data
- Steal customer information
- Process fraudulent refunds
- Crash the application
- Access the database

**TREAT THIS AS A SECURITY BREACH - ACT IMMEDIATELY!**

---

**Created:** 2026-02-08  
**Status:** CRITICAL - EXECUTE IMMEDIATELY  
**Next Review:** After migration complete
