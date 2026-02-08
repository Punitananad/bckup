# ✅ FINAL DEPLOYMENT CHECKLIST
## Complete Migration to New Server

---

## 📊 CURRENT STATUS

✅ **COMPLETED:**
- Django SECRET_KEY changed to: `^u_*nzz-$&m6jeyj=mml8rmp8^7btom(sj9(r3kb8_#uxn$f^*`
- Settings.py updated for PostgreSQL production
- All documentation created

⚠️ **TODO:**
- Change admin password
- Set up PostgreSQL with NEW credentials
- Generate payment gateway keys
- Deploy to new server
- Update DNS

---

## 🎯 COMPLETE DEPLOYMENT SEQUENCE

### PHASE 1: LOCAL PREPARATION (Do Now)

#### ✅ 1. Change Admin Password
```bash
cd application/scan2food
python manage.py changepassword punit
```
**Enter a STRONG password and save it securely**

#### ✅ 2. Update settings.py for Production
**File already updated with:**
- ✅ New SECRET_KEY
- ✅ PostgreSQL configuration
- ✅ Environment variable support

**Still need to add (at end of settings.py):**
```python
# Security Settings for Production
if os.environ.get('DJANGO_ENV') == 'production':
    DEBUG = False
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
```

#### ✅ 3. Test Locally
```bash
cd application/scan2food
python manage.py runserver
```
**Verify it works with SQLite locally**

---

### PHASE 2: SERVER SETUP (On New Server)

#### ✅ 4. Setup New Server
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install python3 python3-pip python3-venv nginx postgresql redis-server -y

# Install certbot for SSL
sudo apt install certbot python3-certbot-nginx -y
```

#### ✅ 5. Setup PostgreSQL
**Follow: POSTGRESQL_SETUP.md**

**Quick commands:**
```bash
# Create database and user
sudo -u postgres psql

CREATE DATABASE scan2food_db;
CREATE USER scan2food_user WITH PASSWORD 'YourStrongPassword123!';
GRANT ALL PRIVILEGES ON DATABASE scan2food_db TO scan2food_user;
\q
```

#### ✅ 6. Setup Redis with Password
```bash
# Edit Redis config
sudo nano /etc/redis/redis.conf

# Add/uncomment:
requirepass YourStrongRedisPassword123!

# Restart Redis
sudo systemctl restart redis

# Test
redis-cli
AUTH YourStrongRedisPassword123!
PING
# Should return: PONG
```

#### ✅ 7. Upload Code to Server
```bash
# On your local machine
scp -r application/scan2food user@YOUR_NEW_IP:/var/www/

# Or use git
ssh user@YOUR_NEW_IP
cd /var/www
git clone YOUR_REPO_URL scan2food
```

#### ✅ 8. Setup Virtual Environment
```bash
cd /var/www/scan2food/application/scan2food
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install python-dotenv
```

#### ✅ 9. Create .env File
```bash
nano .env
```

**Add:**
```env
DJANGO_ENV=production
SECRET_KEY=^u_*nzz-$&m6jeyj=mml8rmp8^7btom(sj9(r3kb8_#uxn$f^*

# Database
DB_NAME=scan2food_db
DB_USER=scan2food_user
DB_PASSWORD=YourStrongPassword123!
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_PASSWORD=YourStrongRedisPassword123!
```

#### ✅ 10. Update settings.py to Load .env
**Add at top of settings.py:**
```python
from dotenv import load_dotenv
load_dotenv()
```

**Update Redis config in settings.py:**
```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
            "password": os.environ.get('REDIS_PASSWORD', ''),
        },
    },
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": os.environ.get('REDIS_PASSWORD', ''),
        }
    }
}
```

#### ✅ 11. Run Migrations
```bash
export DJANGO_ENV=production
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

---

### PHASE 3: PAYMENT GATEWAY SETUP

#### ✅ 12. Generate NEW Payment Gateway Keys

**Razorpay:**
1. Login: https://dashboard.razorpay.com/
2. Settings → API Keys → Generate Live Keys
3. **IMMEDIATELY REVOKE old keys**
4. Save new keys

**Cashfree:**
1. Login: https://merchant.cashfree.com/
2. Developers → Credentials → Generate
3. **IMMEDIATELY REVOKE old keys**
4. Save new keys

**PhonePe:**
1. Contact: merchantsupport@phonepe.com
2. Request new credentials
3. Request revocation of old credentials

#### ✅ 13. Configure in Django Admin
```bash
# Start server temporarily
python manage.py runserver 0.0.0.0:8000

# Login to admin
http://YOUR_SERVER_IP:8000/admin/

# Add payment gateways with NEW credentials
```

---

### PHASE 4: WEB SERVER CONFIGURATION

#### ✅ 14. Setup Daphne Service
```bash
sudo nano /etc/systemd/system/scan2food.service
```

**Add:**
```ini
[Unit]
Description=scan2food Django Application
After=network.target redis.service postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/scan2food/application/scan2food
Environment="PATH=/var/www/scan2food/application/scan2food/venv/bin"
Environment="DJANGO_ENV=production"
EnvironmentFile=/var/www/scan2food/application/scan2food/.env
ExecStart=/var/www/scan2food/application/scan2food/venv/bin/daphne -b 127.0.0.1 -p 8000 theatreApp.asgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl start scan2food
sudo systemctl enable scan2food
sudo systemctl status scan2food
```

#### ✅ 15. Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/scan2food
```

**Add:**
```nginx
upstream scan2food_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name YOUR_NEW_IP scan2food.com www.scan2food.com;

    client_max_body_size 100M;

    location /static/ {
        alias /var/www/scan2food/staticfiles_collected/;
        expires 30d;
    }

    location /media/ {
        alias /var/www/scan2food/application/scan2food/media/;
        expires 30d;
    }

    location /ws/ {
        proxy_pass http://scan2food_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    location / {
        proxy_pass http://scan2food_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/scan2food /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### ✅ 16. Setup SSL Certificate
```bash
sudo certbot --nginx -d scan2food.com -d www.scan2food.com
```

---

### PHASE 5: GO LIVE

#### ✅ 17. Update DNS
**In your domain registrar (GoDaddy, Namecheap, etc.):**
```
Type: A
Name: @
Value: YOUR_NEW_SERVER_IP
TTL: 300

Type: A
Name: www
Value: YOUR_NEW_SERVER_IP
TTL: 300
```

**Wait for DNS propagation (can take 24-48 hours)**

#### ✅ 18. Update Webhook URLs
**In each payment gateway dashboard:**

**Razorpay:**
- Settings → Webhooks
- URL: `https://scan2food.com/theatre/api/razorpay-webhook-url`

**Cashfree:**
- Developers → Webhooks
- URL: `https://scan2food.com/theatre/api/cashfree-data-request`

**PhonePe:**
- Contact support to update webhook URL

#### ✅ 19. Test Everything
```bash
# Test payment flows
# Test order creation
# Test WebSocket connections
# Test admin panel
# Monitor logs
sudo journalctl -u scan2food -f
```

#### ✅ 20. Monitor for 24-48 Hours
- Check error logs
- Monitor transactions
- Verify payments working
- Check customer orders

---

### PHASE 6: CLEANUP

#### ✅ 21. Shut Down Old Server
**Only after confirming everything works:**
```bash
# On old server
sudo systemctl stop daphne
sudo systemctl stop nginx
```

#### ✅ 22. Revoke Old Developer Access
- ✅ All payment gateway keys revoked
- ✅ Old server shut down
- ✅ SSH access removed
- ✅ Database passwords changed

---

## 📝 CREDENTIALS TO SAVE SECURELY

```
=== Django ===
SECRET_KEY: ^u_*nzz-$&m6jeyj=mml8rmp8^7btom(sj9(r3kb8_#uxn$f^*
ADMIN_USER: punit
ADMIN_PASS: [your new password]

=== PostgreSQL ===
DB_NAME: scan2food_db
DB_USER: scan2food_user
DB_PASS: [your strong password]

=== Redis ===
REDIS_PASS: [your strong password]

=== Server ===
NEW_IP: [your new server IP]
SSH_USER: [your username]
SSH_PASS: [your password]

=== Payment Gateways ===
RAZORPAY_KEY: [from dashboard]
RAZORPAY_SECRET: [from dashboard]
CASHFREE_APP_ID: [from dashboard]
CASHFREE_SECRET: [from dashboard]
PHONEPE_MERCHANT_ID: [from support]
PHONEPE_SALT: [from support]
```

**Store in password manager (1Password, LastPass, Bitwarden)**

---

## ✅ FINAL VERIFICATION

- [ ] Django SECRET_KEY changed
- [ ] Admin password changed
- [ ] PostgreSQL setup with NEW credentials
- [ ] Redis password set
- [ ] Payment gateway keys generated and OLD keys revoked
- [ ] Code deployed to new server
- [ ] Migrations completed
- [ ] Static files collected
- [ ] Daphne service running
- [ ] Nginx configured
- [ ] SSL certificate installed
- [ ] DNS updated
- [ ] Webhooks updated
- [ ] All payments tested
- [ ] Old server shut down
- [ ] Old developer has ZERO access

---

## 🎉 SUCCESS!

**When all checkboxes are ticked:**
- ✅ Your site is secure
- ✅ Old developer has no access
- ✅ All credentials are new
- ✅ Payments are working
- ✅ Site is live on new server

---

## 📞 SUPPORT CONTACTS

**Payment Gateways:**
- Razorpay: support@razorpay.com | 1800-102-0480
- Cashfree: care@cashfree.com | 080-68727374
- PhonePe: merchantsupport@phonepe.com

**Emergency:**
- If old developer attacks, immediately revoke all payment keys
- Take old server offline
- Contact payment gateway support

---

**You're ready to deploy! Follow this checklist step by step.**
