# 🚀 scan2food Deployment Guide

## 📋 Quick Overview

**Project Type:** Django Web Application with WebSocket Support  
**Main Apps:** adminPortal, theatre, chat_bot, chat_box, website  
**Database:** SQLite (current) / PostgreSQL (configured)  
**WebSocket:** Django Channels + Redis  
**Server:** Daphne (ASGI)

---

## 🔧 Environment Setup

### 1. Create .env File

Create a `.env` file in `application/scan2food/` directory:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=your-new-ip,your-domain.com

# Database (if using PostgreSQL)
DB_NAME=scan2food_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Redis (for WebSockets)
REDIS_HOST=localhost
REDIS_PORT=6379

# Payment Gateways
RAZORPAY_KEY_ID=your_razorpay_key
RAZORPAY_KEY_SECRET=your_razorpay_secret
CASHFREE_APP_ID=your_cashfree_id
CASHFREE_SECRET_KEY=your_cashfree_secret
PHONEPE_MERCHANT_ID=your_phonepe_merchant_id
PHONEPE_SALT_KEY=your_phonepe_salt
PHONEPE_SALT_INDEX=your_phonepe_index

# Firebase (if using)
FIREBASE_CREDENTIALS_PATH=/path/to/firebase-credentials.json

# Email Settings (if configured)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True

# Security
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
```

### 2. Update settings.py

Add this to your `theatreApp/settings.py`:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Security
SECRET_KEY = os.getenv('SECRET_KEY', 'your-default-secret-key')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')

# Database
if os.getenv('DB_NAME'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }
```

---

## 📦 Installation Steps

### Step 1: System Requirements

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv
sudo apt install redis-server
sudo apt install nginx

# Start Redis
sudo systemctl start redis
sudo systemctl enable redis
```

### Step 2: Clone/Upload Project

```bash
# Upload your project to server
scp -r scan2food/ user@your-server-ip:/var/www/

# Or use git
cd /var/www/
git clone your-repo-url scan2food
```

### Step 3: Create Virtual Environment

```bash
cd /var/www/scan2food/application/scan2food
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install python-dotenv  # For .env support
```

### Step 5: Configure Environment

```bash
# Create .env file
nano .env
# Add all environment variables (see section above)

# Generate new SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 6: Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load initial data (if you have fixtures)
# python manage.py loaddata initial_data.json
```

### Step 7: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

---

## 🌐 Web Server Configuration

### Nginx Configuration

Create `/etc/nginx/sites-available/scan2food`:

```nginx
upstream scan2food_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com your-server-ip;

    client_max_body_size 100M;

    # Static files
    location /static/ {
        alias /var/www/scan2food/staticfiles_collected/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /var/www/scan2food/application/scan2food/media/;
        expires 30d;
    }

    # WebSocket
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

    # Django app
    location / {
        proxy_pass http://scan2food_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/scan2food /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔄 Running the Application

### Option 1: Using Daphne (Recommended for WebSockets)

Create systemd service `/etc/systemd/system/scan2food.service`:

```ini
[Unit]
Description=scan2food Django Application
After=network.target redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/scan2food/application/scan2food
Environment="PATH=/var/www/scan2food/application/scan2food/venv/bin"
ExecStart=/var/www/scan2food/application/scan2food/venv/bin/daphne -b 127.0.0.1 -p 8000 theatreApp.asgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl start scan2food
sudo systemctl enable scan2food
sudo systemctl status scan2food
```

### Option 2: Using Gunicorn (Without WebSockets)

```bash
pip install gunicorn
gunicorn theatreApp.wsgi:application --bind 127.0.0.1:8000 --workers 3
```

---

## 🔒 Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Set DEBUG = False
- [ ] Update ALLOWED_HOSTS with your domain/IP
- [ ] Configure CSRF_TRUSTED_ORIGINS
- [ ] Enable HTTPS with SSL certificate (Let's Encrypt)
- [ ] Set secure cookie flags (SECURE_SSL_REDIRECT, etc.)
- [ ] Configure firewall (UFW)
- [ ] Restrict database access
- [ ] Set proper file permissions
- [ ] Enable Redis password authentication
- [ ] Regular backups of database and media files

---

## 🔍 Troubleshooting

### Check Logs

```bash
# Django logs
sudo journalctl -u scan2food -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Redis logs
sudo tail -f /var/log/redis/redis-server.log
```

### Common Issues

**1. Static files not loading**
```bash
python manage.py collectstatic --clear --noinput
sudo chown -R www-data:www-data /var/www/scan2food/staticfiles_collected/
```

**2. WebSocket connection failed**
```bash
# Check Redis is running
redis-cli ping  # Should return PONG

# Check Daphne is running
sudo systemctl status scan2food
```

**3. Database connection error**
```bash
# Test database connection
python manage.py dbshell
```

**4. Permission denied errors**
```bash
sudo chown -R www-data:www-data /var/www/scan2food/
sudo chmod -R 755 /var/www/scan2food/
```

---

## 📊 Monitoring

### Setup Monitoring

```bash
# Install monitoring tools
pip install sentry-sdk

# Add to settings.py
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

### Health Check Endpoint

Add to `urls.py`:

```python
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({"status": "healthy"})

urlpatterns = [
    path('health/', health_check),
    # ... other patterns
]
```

---

## 🔄 Backup Strategy

### Database Backup

```bash
# SQLite
cp application/scan2food/db.sqlite3 backups/db_$(date +%Y%m%d).sqlite3

# PostgreSQL
pg_dump -U your_user scan2food_db > backup_$(date +%Y%m%d).sql
```

### Media Files Backup

```bash
tar -czf media_backup_$(date +%Y%m%d).tar.gz application/scan2food/media/
```

### Automated Backup Script

Create `/var/www/scan2food/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/scan2food"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
cp /var/www/scan2food/application/scan2food/db.sqlite3 $BACKUP_DIR/db_$DATE.sqlite3

# Backup media
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /var/www/scan2food/application/scan2food/media/

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete
```

Add to crontab:

```bash
crontab -e
# Add: 0 2 * * * /var/www/scan2food/backup.sh
```

---

## 📞 Support

For issues or questions:
1. Check logs first
2. Review Django documentation
3. Check Channels documentation for WebSocket issues
4. Review this deployment guide

---

**Last Updated:** 2026-02-08
