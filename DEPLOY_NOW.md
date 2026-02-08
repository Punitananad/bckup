# 🚀 DEPLOY TO NEW SERVER - Step by Step

## 📋 INFORMATION NEEDED

Before we start, gather this information:

```
NEW_SERVER_IP: ___________________
SSH_USERNAME: ___________________
SSH_PASSWORD: ___________________
```

---

## 🎯 DEPLOYMENT STEPS

### STEP 1: Connect to Your Server

**From your Windows machine:**

```bash
# Using PowerShell or CMD
ssh username@YOUR_NEW_SERVER_IP

# Example:
# ssh root@165.22.123.45
```

**First time connecting?**
- It will ask: "Are you sure you want to continue connecting?"
- Type: `yes`
- Enter your password

---

### STEP 2: Update System

**Run these commands on the server:**

```bash
# Update package list
sudo apt update

# Upgrade packages
sudo apt upgrade -y

# Install basic tools
sudo apt install -y git curl wget vim
```

---

### STEP 3: Install Required Software

```bash
# Install Python and pip
sudo apt install -y python3 python3-pip python3-venv

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Install Redis
sudo apt install -y redis-server

# Install Nginx
sudo apt install -y nginx

# Install certbot for SSL
sudo apt install -y certbot python3-certbot-nginx
```

---

### STEP 4: Setup PostgreSQL

```bash
# Switch to postgres user
sudo -u postgres psql
```

**In PostgreSQL prompt, run:**

```sql
-- Create database
CREATE DATABASE scan2food_db;

-- Create user with STRONG password
CREATE USER scan2food_user WITH PASSWORD 'YourStrongPassword123!@#';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE scan2food_db TO scan2food_user;

-- Connect to database
\c scan2food_db

-- Grant schema permissions
GRANT ALL ON SCHEMA public TO scan2food_user;

-- Exit
\q
```

**Save these credentials:**
```
DB_NAME: scan2food_db
DB_USER: scan2food_user
DB_PASSWORD: YourStrongPassword123!@#
```

---

### STEP 5: Setup Redis Password

```bash
# Edit Redis config
sudo nano /etc/redis/redis.conf
```

**Find this line (around line 790):**
```
# requirepass foobared
```

**Change to:**
```
requirepass YourStrongRedisPassword123!
```

**Save:** Press `Ctrl+X`, then `Y`, then `Enter`

**Restart Redis:**
```bash
sudo systemctl restart redis
sudo systemctl enable redis
```

**Test Redis:**
```bash
redis-cli
AUTH YourStrongRedisPassword123!
PING
# Should return: PONG
exit
```

**Save this credential:**
```
REDIS_PASSWORD: YourStrongRedisPassword123!
```

---

### STEP 6: Upload Your Code

**Option A: Using Git (Recommended)**

```bash
# On server
cd /var/www
sudo mkdir -p scan2food
sudo chown $USER:$USER scan2food

# If you have git repo
git clone YOUR_REPO_URL scan2food

# Or create empty directory for manual upload
cd scan2food
```

**Option B: Upload from Windows**

**On your Windows machine (PowerShell):**

```powershell
# Navigate to your project
cd C:\Users\punit\Downloads\Documents\Desktop\s2f_bp

# Upload to server
scp -r application username@YOUR_SERVER_IP:/var/www/scan2food/

# Example:
# scp -r application root@165.22.123.45:/var/www/scan2food/
```

---

### STEP 7: Setup Virtual Environment

**On server:**

```bash
cd /var/www/scan2food/application/scan2food

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install additional packages
pip install python-dotenv gunicorn
```

---

### STEP 8: Create .env File

```bash
cd /var/www/scan2food/application/scan2food
nano .env
```

**Add this content:**

```env
DJANGO_ENV=production

# Django
SECRET_KEY=^u_*nzz-$&m6jeyj=mml8rmp8^7btom(sj9(r3kb8_#uxn$f^*

# Database
DB_NAME=scan2food_db
DB_USER=scan2food_user
DB_PASSWORD=YourStrongPassword123!@#
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_PASSWORD=YourStrongRedisPassword123!
```

**Save:** Press `Ctrl+X`, then `Y`, then `Enter`

---

### STEP 9: Update settings.py

**Make sure settings.py loads .env:**

```bash
nano theatreApp/settings.py
```

**At the very top, add:**

```python
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
```

**Update ALLOWED_HOSTS (around line 26):**

```python
ALLOWED_HOSTS = [
    'YOUR_NEW_SERVER_IP',  # Add your new IP
    'scan2food.com',
    'www.scan2food.com',
    'localhost',
]
```

**Update Redis config (around line 100):**

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

**Save and exit**

---

### STEP 10: Run Migrations

```bash
cd /var/www/scan2food/application/scan2food
source venv/bin/activate

# Set environment
export DJANGO_ENV=production

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
# Username: punit
# Email: punitanand146@gmail.com
# Password: [your new password from earlier]

# Collect static files
python manage.py collectstatic --noinput
```

---

### STEP 11: Setup Daphne Service

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
EnvironmentFile=/var/www/scan2food/application/scan2food/.env
ExecStart=/var/www/scan2food/application/scan2food/venv/bin/daphne -b 127.0.0.1 -p 8000 theatreApp.asgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Set permissions:**

```bash
sudo chown -R www-data:www-data /var/www/scan2food
sudo chmod -R 755 /var/www/scan2food
```

**Start service:**

```bash
sudo systemctl daemon-reload
sudo systemctl start scan2food
sudo systemctl enable scan2food
sudo systemctl status scan2food
```

**Should show:** `Active: active (running)`

---

### STEP 12: Configure Nginx

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
    server_name YOUR_NEW_SERVER_IP scan2food.com www.scan2food.com;

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
        proxy_read_timeout 86400;
    }

    location / {
        proxy_pass http://scan2food_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

**Enable site:**

```bash
sudo ln -s /etc/nginx/sites-available/scan2food /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

### STEP 13: Test the Site

**Open browser:**
```
http://YOUR_NEW_SERVER_IP
```

**You should see your site!**

**Test admin:**
```
http://YOUR_NEW_SERVER_IP/admin/
```

**Login with:**
- Username: `punit`
- Password: [your new password]

---

### STEP 14: Setup SSL (After DNS is updated)

**After you update DNS to point to new server:**

```bash
sudo certbot --nginx -d scan2food.com -d www.scan2food.com
```

---

## ✅ DEPLOYMENT CHECKLIST

- [ ] Connected to new server
- [ ] System updated
- [ ] PostgreSQL installed and configured
- [ ] Redis installed with password
- [ ] Code uploaded to server
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] .env file created
- [ ] settings.py updated
- [ ] Migrations completed
- [ ] Superuser created
- [ ] Static files collected
- [ ] Daphne service running
- [ ] Nginx configured
- [ ] Site accessible via IP
- [ ] Admin panel working

---

## 🎯 NEXT STEPS AFTER DEPLOYMENT

1. **Configure Payment Gateways** in admin panel
2. **Update DNS** to point to new IP
3. **Setup SSL** certificate
4. **Update webhooks** in payment gateways
5. **Test all payment flows**
6. **Monitor for 24-48 hours**
7. **Shut down old server**

---

## 🆘 TROUBLESHOOTING

**Service not starting?**
```bash
sudo journalctl -u scan2food -n 50
```

**Nginx error?**
```bash
sudo tail -f /var/log/nginx/error.log
```

**Database connection error?**
```bash
psql -U scan2food_user -d scan2food_db -h localhost
```

---

**Ready to start? Begin with STEP 1!**
