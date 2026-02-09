# 🔐 SCAN2FOOD - COMPLETE CREDENTIALS & INFORMATION
**Date Created:** February 8, 2026  
**Status:** PRODUCTION - LIVE

---

## 🌐 SERVER INFORMATION

### Production Server
```
Server IP: 165.22.219.111
Operating System: Ubuntu 24.04 LTS
Server Provider: DigitalOcean (or your provider)
Server Location: Bangalore, India

SSH Access:
ssh root@165.22.219.111
Password: [Your SSH password]
```

### Domain Information
```
Domain: scan2food.com
DNS Provider: [Your DNS provider]
Current DNS: Points to 165.22.219.111
```

---

## 🔑 DJANGO APPLICATION

### Django Admin Panel

**Production:**
```
Django Admin (Superuser):
URL: http://165.22.219.111/admin/
Username: punit
Email: punitanand146@gmail.com
Password: [Your admin password]

Admin Portal (Service Provider Dashboard):
URL: http://165.22.219.111/admin-portal/
Username: punit
Password: [Your admin password]
Note: After login, superusers and service_provider group users are automatically redirected here
```

**Localhost (Development):**
```
Django Admin (Superuser):
URL: http://localhost:8000/admin/
Username: punit
Email: punitanand146@gmail.com
Password: [Your admin password]

Admin Portal (Service Provider Dashboard):
URL: http://localhost:8000/admin-portal/
Username: punit
Password: [Your admin password]
Note: After login at http://localhost:8000/login, you'll be redirected to admin portal
```

### Django Secret Key
```
SECRET_KEY: ^u_*nzz-$&m6jeyj=mml8rmp8^7btom(sj9(r3kb8_#uxn$f^*
```

### Application Paths
```
Project Root: /var/www/scan2food/
Django Root: /var/www/scan2food/application/scan2food/
Virtual Environment: /var/www/scan2food/application/scan2food/venv/
Static Files: /var/www/scan2food/application/scan2food/staticfiles/
Media Files: /var/www/scan2food/application/scan2food/media/
```

---

## 🗄️ DATABASE CREDENTIALS

### PostgreSQL Database
```
Database Name: scan2food_db
Database User: scan2food_user
Database Password: scann2Food
Database Host: 127.0.0.1
Database Port: 5432

Connection Command:
psql -U scan2food_user -d scan2food_db -h 127.0.0.1
```

### Database Backup Location
```
Backup Directory: /var/www/scan2food/application/scan2food/media/backup_db/
Backup Script: /var/www/scan2food/application/scan2food/backupScript/db_backup.py
```

---

## 🔴 REDIS CREDENTIALS

### Redis Configuration
```
Redis Host: 127.0.0.1
Redis Port: 6379
Redis Password: scann2Food

Test Connection:
redis-cli
AUTH scann2Food
PING
```

---

## 💳 PAYMENT GATEWAY CREDENTIALS

### Razorpay
```
Dashboard: https://dashboard.razorpay.com/
Login Email: [Owner's email]
Login Password: [Owner's password]

API Credentials:
Key ID: [Generate NEW key from dashboard]
Key Secret: [Generate NEW secret from dashboard]

Webhook URL: https://scan2food.com/theatre/api/razorpay-webhook-url
```

### Cashfree
```
Dashboard: https://merchant.cashfree.com/
Login Email: [Owner's email]
Login Password: [Owner's password]

API Credentials:
App ID: [Generate NEW from dashboard]
Secret Key: [Generate NEW from dashboard]

Webhook URL: https://scan2food.com/theatre/api/cashfree-data-request
```

### PhonePe
```
Support Email: merchantsupport@phonepe.com
Login: [Contact PhonePe support]

API Credentials:
Merchant ID: [Get from PhonePe]
Salt Key: [Get from PhonePe]
Salt Index: [Get from PhonePe]

Webhook URL: https://scan2food.com/theatre/api/phonepe-data-request
```

### PayU (if used)
```
Dashboard: https://onboarding.payu.in/
Login Email: [Owner's email]

API Credentials:
Merchant Key: [From dashboard]
Salt: [From dashboard]

Webhook URL: https://scan2food.com/theatre/api/payu-webhook-url
```

### CCAvenue (if used)
```
Dashboard: https://dashboard.ccavenue.com/
Login Email: [Owner's email]

API Credentials:
Merchant ID: [From dashboard]
Working Key: [From dashboard]

Webhook URL: https://scan2food.com/theatre/api/ccavenue-hook
```

---

## 📁 GITHUB REPOSITORY

### Repository Information
```
Repository URL: https://github.com/Punitananad/bckup.git
Repository Name: bckup
Visibility: Private
Owner: Punitananad

Clone Command:
git clone https://github.com/Punitananad/bckup.git
```

### GitHub Credentials
```
Username: Punitananad
Email: punitanand146@gmail.com
Password/Token: [Your GitHub password or Personal Access Token]
```

---

## 🔧 SYSTEM SERVICES

### Daphne Service (Django Application)
```
Service Name: scan2food.service
Service File: /etc/systemd/system/scan2food.service
Status: systemctl status scan2food
Start: systemctl start scan2food
Stop: systemctl stop scan2food
Restart: systemctl restart scan2food
Logs: journalctl -u scan2food -f
```

### Nginx Web Server
```
Config File: /etc/nginx/sites-available/scan2food
Enabled: /etc/nginx/sites-enabled/scan2food
Test Config: nginx -t
Restart: systemctl restart nginx
Logs: tail -f /var/log/nginx/error.log
```

### PostgreSQL Database
```
Status: systemctl status postgresql
Start: systemctl start postgresql
Restart: systemctl restart postgresql
```

### Redis Server
```
Status: systemctl status redis
Start: systemctl start redis
Restart: systemctl restart redis
Config: /etc/redis/redis.conf
```

---

## 📧 EMAIL CONFIGURATION (if configured)

### Email Settings
```
Email Host: smtp.gmail.com
Email Port: 587
Email User: [Your email]
Email Password: [App-specific password]
Use TLS: True
```

---

## 🔒 SSL CERTIFICATE (After DNS Update)

### Let's Encrypt SSL
```
Install Command:
sudo certbot --nginx -d scan2food.com -d www.scan2food.com

Certificate Location: /etc/letsencrypt/live/scan2food.com/
Auto-Renewal: Enabled (certbot renew)
```

---

## 🚀 DEPLOYMENT COMMANDS

### Update Code from GitHub
```bash
cd /var/www/scan2food
git pull origin main
source application/scan2food/venv/bin/activate
cd application/scan2food
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart scan2food
sudo systemctl restart nginx
```

### View Application Logs
```bash
# Daphne logs
sudo journalctl -u scan2food -f

# Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Nginx access logs
sudo tail -f /var/log/nginx/access.log
```

### Database Backup
```bash
cd /var/www/scan2food/application/scan2food
source venv/bin/activate
python backupScript/db_backup.py
```

### Manual Database Backup
```bash
pg_dump -U scan2food_user -d scan2food_db > backup_$(date +%Y%m%d).sql
```

---

## 🔐 ENVIRONMENT VARIABLES (.env file)

### Location
```
/var/www/scan2food/application/scan2food/.env
```

### Content
```env
DJANGO_ENV=production
SECRET_KEY=^u_*nzz-$&m6jeyj=mml8rmp8^7btom(sj9(r3kb8_#uxn$f^*

DB_NAME=scan2food_db
DB_USER=scan2food_user
DB_PASSWORD=scann2Food
DB_HOST=127.0.0.1
DB_PORT=5432

REDIS_PASSWORD=scann2Food
```

---

## ⚠️ OLD SERVER (TO BE SHUT DOWN)

### Old Server Information
```
Old Server IP: 134.209.149.31
Status: ACTIVE (shut down after migration complete)
Old Developer Access: YES (security risk)

Old Database Credentials (COMPROMISED):
Database: app
Username: guru
Password: guru@2003

Action Required:
1. Test new server thoroughly
2. Monitor for 24-48 hours
3. Shut down old server
4. Revoke old payment gateway keys
```

---

## 📞 SUPPORT CONTACTS

### Payment Gateway Support
```
Razorpay:
- Email: support@razorpay.com
- Phone: 1800-102-0480

Cashfree:
- Email: care@cashfree.com
- Phone: 080-68727374

PhonePe:
- Email: merchantsupport@phonepe.com
```

### Server Provider Support
```
[Your hosting provider contact information]
```

---

## ✅ POST-DEPLOYMENT CHECKLIST

### Immediate Actions
- [ ] Generate NEW payment gateway keys
- [ ] Update payment gateways in admin panel
- [ ] REVOKE old payment gateway keys
- [ ] Test all payment flows
- [ ] Test order creation
- [ ] Test WebSocket features

### Within 24 Hours
- [ ] Update DNS to point to new server
- [ ] Setup SSL certificate
- [ ] Update webhook URLs in payment gateways
- [ ] Monitor error logs
- [ ] Test from multiple devices

### Within 48 Hours
- [ ] Verify all features working
- [ ] Check database backups
- [ ] Monitor transaction processing
- [ ] Shut down old server
- [ ] Remove old developer access

---

## 🔒 SECURITY NOTES

### What Old Developer Knows (COMPROMISED)
```
❌ Old SECRET_KEY: django-insecure-a@q^h)$szzhw_$wd)0zu@8x^woi^d9vufw#^!-uuhv2%j2r%*e
❌ Old DB User: guru
❌ Old DB Password: guru@2003
❌ Old Server IP: 134.209.149.31
❌ Old payment gateway keys (until you revoke them)
```

### What Old Developer DOES NOT Know (SECURE)
```
✅ New SECRET_KEY
✅ New database credentials
✅ New server IP and access
✅ New admin password
✅ New payment gateway keys (after you change them)
```

---

## 📝 IMPORTANT REMINDERS

1. **NEVER commit .env file to GitHub**
2. **NEVER share these credentials publicly**
3. **Store this file in a secure password manager**
4. **Change payment gateway keys IMMEDIATELY**
5. **Revoke old payment gateway keys**
6. **Monitor logs for suspicious activity**
7. **Keep regular database backups**
8. **Update this file when credentials change**

---

## 🆘 EMERGENCY PROCEDURES

### If Site Goes Down
```bash
# Check service status
sudo systemctl status scan2food
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis

# Restart services
sudo systemctl restart scan2food
sudo systemctl restart nginx

# Check logs
sudo journalctl -u scan2food -n 100
sudo tail -f /var/log/nginx/error.log
```

### If Database Connection Fails
```bash
# Test database connection
psql -U scan2food_user -d scan2food_db -h 127.0.0.1

# Check PostgreSQL status
sudo systemctl status postgresql

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### If Old Developer Attacks
```
1. Immediately revoke ALL payment gateway keys
2. Change database password
3. Take old server offline
4. Contact payment gateway support
5. Monitor transactions closely
6. Restore from backup if needed
```

---

**KEEP THIS FILE SECURE AND PRIVATE!**

**Last Updated:** February 8, 2026  
**Next Review:** After DNS update and SSL setup
