# 🔑 GENERATE NEW KEYS - Complete Guide
## Fresh Start with All New Credentials

---

## 🎯 STRATEGY: Generate Everything Fresh

**Advantage:** Old developer has ZERO access to anything  
**Requirement:** Owner must have access to payment gateway accounts

---

## 📋 STEP-BY-STEP GUIDE

### ✅ STEP 1: Generate New Django SECRET_KEY

**Run this command:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Example output:**
```
django-insecure-x7k#9m@2$vn8w!p4q&5r*t6y^u8i(o0p-a=s+d_f:g;h<j>k
```

**Update file:** `application/scan2food/theatreApp/settings.py`

**Change line 21 from:**
```python
SECRET_KEY = 'django-insecure-a@q^h)$szzhw_$wd)0zu@8x^woi^d9vufw#^!-uuhv2%j2r%*e'
```

**To:**
```python
SECRET_KEY = 'YOUR_NEW_GENERATED_KEY_HERE'
```

✅ **Done!** Old sessions are now invalid.

---

### ✅ STEP 2: Change Admin Password

**Run this command:**
```bash
cd application/scan2food
python manage.py changepassword punit
```

**It will ask:**
```
Password: [enter new password]
Password (again): [enter same password]
```

**Choose a STRONG password:**
- At least 12 characters
- Mix of uppercase, lowercase, numbers, symbols
- Example: `Scan2Food@2026!Secure`

✅ **Done!** Old developer can't login to admin panel.

---

### ✅ STEP 3: Generate NEW Payment Gateway Keys

#### 3.1 RAZORPAY

**Login to Razorpay Dashboard:**
- URL: https://dashboard.razorpay.com/
- Use owner's credentials

**Generate NEW Keys:**
1. Go to: **Settings** → **API Keys**
2. Click: **Generate Test Keys** (for testing) or **Generate Live Keys** (for production)
3. You'll get:
   - **Key ID:** `rzp_test_xxxxxxxxxxxxx` or `rzp_live_xxxxxxxxxxxxx`
   - **Key Secret:** `xxxxxxxxxxxxxxxxxxxxxxxx`
4. **COPY THESE IMMEDIATELY** - Secret is shown only once!

**REVOKE Old Keys:**
1. In same page, find old keys
2. Click **Regenerate** or **Delete**
3. Confirm deletion

**Save these values:**
```
RAZORPAY_KEY_ID=rzp_live_xxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx
```

---

#### 3.2 CASHFREE

**Login to Cashfree Dashboard:**
- URL: https://merchant.cashfree.com/
- Use owner's credentials

**Generate NEW Keys:**
1. Go to: **Developers** → **Credentials**
2. Select: **Production** or **Sandbox**
3. Click: **Generate Credentials**
4. You'll get:
   - **App ID:** `xxxxxxxxxxxxxxxxxxxxxxxx`
   - **Secret Key:** `xxxxxxxxxxxxxxxxxxxxxxxx`

**REVOKE Old Keys:**
1. Click on old credentials
2. Click **Revoke** or **Delete**
3. Confirm

**Save these values:**
```
CASHFREE_APP_ID=xxxxxxxxxxxxxxxxxxxxxxxx
CASHFREE_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
```

---

#### 3.3 PHONEPE

**Contact PhonePe Support:**
- Email: merchantsupport@phonepe.com
- Phone: Check PhonePe merchant portal

**Request:**
1. Generate NEW Merchant ID and Salt Key
2. Revoke OLD credentials
3. Update webhook URLs to new server

**You'll receive:**
```
PHONEPE_MERCHANT_ID=MERCHANTUAT or M_XXXXXX
PHONEPE_SALT_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
PHONEPE_SALT_INDEX=1
```

---

#### 3.4 PAYU (if used)

**Login to PayU Dashboard:**
- URL: https://onboarding.payu.in/
- Use owner's credentials

**Generate NEW Keys:**
1. Go to: **Settings** → **Account Details**
2. Find: **Merchant Key** and **Salt**
3. Request new credentials from support if needed

**You'll get:**
```
PAYU_MERCHANT_KEY=xxxxxxxx
PAYU_SALT=xxxxxxxx
```

---

#### 3.5 CCAVENUE (if used)

**Login to CCAvenue Dashboard:**
- URL: https://dashboard.ccavenue.com/
- Use owner's credentials

**Generate NEW Keys:**
1. Go to: **Settings** → **Generate Working Key**
2. You'll get:
   - **Merchant ID:** `xxxxxx`
   - **Working Key:** `xxxxxxxxxxxxxxxxxxxxxxxx`

**Save these values:**
```
CCAVENUE_MERCHANT_ID=xxxxxx
CCAVENUE_WORKING_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
```

---

### ✅ STEP 4: Update settings.py for Production

**File:** `application/scan2food/theatreApp/settings.py`

**Make these changes:**

```python
# Line 21: NEW SECRET_KEY
SECRET_KEY = 'your-new-generated-secret-key-here'

# Line 24: Set DEBUG to False for production
DEBUG = False

# Line 26: Update ALLOWED_HOSTS with NEW server IP
ALLOWED_HOSTS = [
    'YOUR_NEW_SERVER_IP',  # Add your new IP here
    'scan2food.com', 
    'www.scan2food.com', 
    'localhost',  # Keep for local testing
    '127.0.0.1'   # Keep for local testing
]

# Add these security settings at the end of file:
# Security Settings for Production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = [
    'https://scan2food.com',
    'https://www.scan2food.com',
]
```

---

### ✅ STEP 5: Configure Payment Gateways in Django Admin

**After deploying to new server:**

1. **Start the server:**
   ```bash
   cd application/scan2food
   python manage.py runserver 0.0.0.0:8000
   ```

2. **Login to Admin:**
   - URL: `http://YOUR_SERVER_IP:8000/admin/`
   - Username: `punit`
   - Password: [your new password]

3. **Add Payment Gateways:**
   - Go to: **Admin Portal** → **Payment Gateways**
   - Click: **Add Payment Gateway**

**For Razorpay:**
```
Name: Razorpay
Gateway Key: rzp_live_xxxxxxxxxxxxx
Gateway Secret: xxxxxxxxxxxxxxxxxxxxxxxx
Is Active: ✓
```

**For Split Razorpay (if using):**
```
Name: split_razorpay
Gateway Key: rzp_live_xxxxxxxxxxxxx
Gateway Secret: xxxxxxxxxxxxxxxxxxxxxxxx
Is Active: ✓
```

**For Cashfree:**
```
Name: Cashfree
Gateway Key: [App ID]
Gateway Secret: [Secret Key]
Is Active: ✓
```

**For PhonePe:**
```
Name: Phonepe
Gateway Key: [Merchant ID]
Gateway Secret: [Salt Key]
Is Active: ✓
```

**For PayU:**
```
Name: PayU
Gateway Key: [Merchant Key]
Gateway Secret: [Not used for PayU]
Gateway Salt: [Salt]
Is Active: ✓
```

---

### ✅ STEP 6: Update Webhook URLs in Payment Gateways

**After DNS points to new server, update webhooks:**

#### Razorpay Webhooks:
1. Login: https://dashboard.razorpay.com/
2. Go to: **Settings** → **Webhooks**
3. Update URL to: `https://scan2food.com/theatre/api/razorpay-webhook-url`
4. Select events: `payment.captured`, `payment.failed`
5. Save

#### Cashfree Webhooks:
1. Login: https://merchant.cashfree.com/
2. Go to: **Developers** → **Webhooks**
3. Update URL to: `https://scan2food.com/theatre/api/cashfree-data-request`
4. Save

#### PhonePe Webhooks:
1. Contact PhonePe support
2. Request webhook URL update to: `https://scan2food.com/theatre/api/phonepe-data-request`

---

### ✅ STEP 7: Set Redis Password

**On your server, edit Redis config:**
```bash
sudo nano /etc/redis/redis.conf
```

**Find and uncomment/add:**
```
requirepass YourStrongRedisPassword123!
```

**Restart Redis:**
```bash
sudo systemctl restart redis
```

**Update settings.py:**
```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
            "password": "YourStrongRedisPassword123!",
        },
    },
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": "YourStrongRedisPassword123!",
        }
    }
}
```

---

### ✅ STEP 8: Database Migration (if using PostgreSQL)

**Create new database user:**
```sql
-- Login to PostgreSQL
sudo -u postgres psql

-- Create new user
CREATE USER scan2food_new WITH PASSWORD 'YourStrongDBPassword123!';

-- Create database
CREATE DATABASE scan2food_db OWNER scan2food_new;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE scan2food_db TO scan2food_new;

-- Exit
\q
```

**Update settings.py:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'scan2food_db',
        'USER': 'scan2food_new',
        'PASSWORD': 'YourStrongDBPassword123!',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## 📝 CREDENTIALS CHECKLIST

Create a secure document with all new credentials:

```
=== DJANGO ===
SECRET_KEY: [your new key]
ADMIN_USERNAME: punit
ADMIN_PASSWORD: [your new password]

=== DATABASE ===
DB_NAME: scan2food_db
DB_USER: scan2food_new
DB_PASSWORD: [your new password]
DB_HOST: localhost
DB_PORT: 5432

=== REDIS ===
REDIS_HOST: 127.0.0.1
REDIS_PORT: 6379
REDIS_PASSWORD: [your new password]

=== RAZORPAY ===
KEY_ID: [from dashboard]
KEY_SECRET: [from dashboard]

=== CASHFREE ===
APP_ID: [from dashboard]
SECRET_KEY: [from dashboard]

=== PHONEPE ===
MERCHANT_ID: [from support]
SALT_KEY: [from support]
SALT_INDEX: [from support]

=== PAYU ===
MERCHANT_KEY: [from dashboard]
SALT: [from dashboard]

=== CCAVENUE ===
MERCHANT_ID: [from dashboard]
WORKING_KEY: [from dashboard]

=== SERVER ===
NEW_IP: [your new server IP]
SSH_USER: [your username]
SSH_PASSWORD: [your new password]
```

**Store this document:**
- ✅ In password manager (1Password, LastPass, Bitwarden)
- ✅ Encrypted file on secure location
- ❌ NOT in code repository
- ❌ NOT in email or chat

---

## 🚀 DEPLOYMENT SEQUENCE

### Phase 1: Preparation
1. ✅ Generate all new keys (above steps)
2. ✅ Update settings.py with new values
3. ✅ Test locally with new keys

### Phase 2: Server Setup
4. ✅ Setup new server
5. ✅ Install dependencies
6. ✅ Configure Redis with password
7. ✅ Setup PostgreSQL with new user

### Phase 3: Deploy
8. ✅ Upload code to new server
9. ✅ Run migrations
10. ✅ Create superuser
11. ✅ Configure payment gateways in admin
12. ✅ Test payment flows

### Phase 4: Go Live
13. ✅ Update DNS to new IP
14. ✅ Update webhooks in payment gateways
15. ✅ Monitor for 24 hours
16. ✅ Shut down old server

---

## ⚠️ IMPORTANT REMINDERS

1. **NEVER share new credentials with old developer**
2. **Test each payment gateway before going live**
3. **Keep backup of all credentials**
4. **Monitor transactions closely for first week**
5. **Document everything you do**

---

## 🆘 IF SOMETHING GOES WRONG

### Payment not working:
- Check webhook URLs are correct
- Verify API keys are active
- Check payment gateway dashboard for errors

### Can't login to admin:
- Reset password: `python manage.py changepassword punit`

### Redis connection error:
- Check Redis is running: `sudo systemctl status redis`
- Verify password in settings.py matches redis.conf

### Database connection error:
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify credentials in settings.py

---

**You're now ready to generate all new keys and deploy securely!**

**Next step:** Start with STEP 1 (Generate SECRET_KEY) and work through each step.
