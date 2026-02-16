# API Key Security Deployment Guide

## ⚠️ MIDDLEWARE NOT WORKING? SEE FIX BELOW ⚠️

**If middleware is deployed but not blocking requests without API key:**

See detailed fix guide: **DEPLOY_MIDDLEWARE_FIX.md**

Quick diagnostic:
```bash
# On production server - run diagnostic
bash diagnose_middleware.sh
```

Quick fix:
```bash
# On production server - fix and restart
cd /var/www/scan2food
git pull origin main
sudo systemctl daemon-reload
find application/scan2food -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
sudo systemctl restart gunicorn && sudo systemctl restart daphne
curl -i https://scan2food.com/theatre/api/theatre-detail  # Should return 401
```

---

## Overview
This guide explains how to deploy the API key authentication system that protects your public customer-facing endpoints from unauthorized access.

## What Was Implemented

### 1. API Key Middleware
- **File**: `application/scan2food/theatreApp/middleware.py`
- **Purpose**: Validates API keys on all public customer endpoints
- **Protection**: Blocks unauthorized access while allowing webhooks and authenticated staff

### 2. Protected Endpoints
The following customer-facing endpoints now require an API key:
- `/theatre/api/all-menu/<pk>` - Menu data
- `/theatre/api/create-order` - Order creation
- `/theatre/api/theatre-detail` - Theatre information
- `/theatre/api/tax-list/<pk>` - Tax information
- `/theatre/api/order-data/<pk>` - Order details
- `/theatre/api/seat-last-order/<pk>` - Seat order status
- `/theatre/api/get-payu-form-details/<pk>` - Payment form data
- `/theatre/show-menu/<pk>` - Menu page
- `/theatre/order-status/<pk>` - Order status page
- `/theatre/order-feedback/<pk>` - Order feedback page

### 3. Excluded Endpoints (No API Key Required)
- **Webhooks**: All payment gateway webhooks (use signature verification)
- **Admin**: Django admin panel
- **Static/Media**: Static and media files
- **Authentication**: Login/logout pages
- **Staff**: Any request from authenticated theatre staff

## Deployment Steps

### Step 1: Generate Secure API Key

On your server, run:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

This will output something like:
```
a8f3d9e2b7c4f1a6e9d2c5b8a1f4e7d0k3m9n2p5q8r1s4t7u0v3w6x9y2z5
```

**IMPORTANT**: Save this key securely - you'll need it for the next step.

### Step 2: Update Environment Variables

#### For Production Server:

1. SSH into your server:
```bash
ssh root@your-server-ip
```

2. Navigate to your project directory:
```bash
cd /var/www/scan2food
```

3. Create or edit the `.env` file:
```bash
nano application/scan2food/.env
```

4. Add the API key (use the key you generated in Step 1):
```bash
API_KEY=a8f3d9e2b7c4f1a6e9d2c5b8a1f4e7d0k3m9n2p5q8r1s4t7u0v3w6x9y2z5
```

5. Save and exit (Ctrl+X, then Y, then Enter)

#### For Local Development:

1. Open `application/scan2food/.env` (create if it doesn't exist)
2. Add:
```bash
API_KEY=your_local_dev_key_here
```

### Step 3: Deploy Code Changes

#### Option A: Using Git (Recommended)

```bash
# On your local machine, commit and push changes
git add .
git commit -m "Add API key authentication for public endpoints"
git push origin main
pu-1gb-amd-blr1-01:~# cd /var/www/scan2food#
-bash: cd: /var/www/scan2food#: No such file or directory
root@ubuntu-s-1vcpu-1gb-amd-blr1-01:~# cd /var/www/scan2food
root@ubuntu-s-1vcpu-1gb-amd-blr1-01:/var/www/scan2food# journalctl -u gunicorn -n 50 --no-pager
Feb 15 04:46:34 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[184159]: Forbidden (Referer checking failed - no Referer.): /
Feb 15 05:14:21 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[184159]: Not Found: /.env
Feb 15 05:14:23 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[184158]: Forbidden (Referer checking failed - no Referer.): /
Feb 15 05:41:36 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[184159]: Not Found: /xsq
Feb 15 05:41:36 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[184158]: Not Found: /favicon.ico        
Feb 15 05:48:01 ubuntu-s-1vcpu-1gb-amd-blr1-01 systemd[1]: Stopping gunicorn.service...
Feb 15 05:48:01 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[184154]: [2026-02-15 05:48:01 +0000] [184154] [INFO] Handling signal: term
Feb 15 05:48:02 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[184159]: [2026-02-15 11:18:02 +0530] [184159] [INFO] Worker exiting (pid: 184159)
Feb 15 05:48:02 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[184158]: [2026-02-15 11:18:02 +0530] [184158] [INFO] Worker exiting (pid: 184158)
Feb 15 05:48:04 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[184154]: [2026-02-15 05:48:04 +0000] [184154] [INFO] Shutting down: Master
Feb 15 05:48:04 ubuntu-s-1vcpu-1gb-amd-blr1-01 systemd[1]: gunicorn.service: Deactivated successfully.
Feb 15 05:48:04 ubuntu-s-1vcpu-1gb-amd-blr1-01 systemd[1]: Stopped gunicorn.service.
Feb 15 05:48:04 ubuntu-s-1vcpu-1gb-amd-blr1-01 systemd[1]: gunicorn.service: Consumed 1min 29.331s CPU time, 293.4M memory peak, 0B memory swap peak.
Feb 15 05:48:04 ubuntu-s-1vcpu-1gb-amd-blr1-01 systemd[1]: Started gunicorn.service.
Feb 15 05:48:04 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[216199]: [2026-02-15 05:48:04 +0000] [216199] [INFO] Starting gunicorn 25.0.3
Feb 15 05:48:04 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[216199]: [2026-02-15 05:48:04 +0000] [216199] [INFO] Listening at: unix:/var/www/scan2food/application/scan2food/gunicorn.sock (216199) 
Feb 15 05:48:04 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[216199]: [2026-02-15 05:48:04 +0000] [216199] [INFO] Using worker: sync
Feb 15 05:48:04 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[216201]: [2026-02-15 05:48:04 +0000] [216201] [INFO] Booting worker with pid: 216201
Feb 15 05:48:04 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[216202]: [2026-02-15 05:48:04 +0000] [216202] [INFO] Booting worker with pid: 216202
Feb 15 05:48:37 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[216202]: /var/www/scan2food/application/scan2food/venv/lib/python3.12/site-packages/django/db/models/fields/__init__.py:1670: RuntimeWarning: DateTimeField Order.start_time received a naive datetime (2026-02-15 06:00:00) while time zone support is active.
Feb 15 05:48:37 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[216202]:   warnings.warn(
Feb 15 05:48:37 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[216202]: /var/www/scan2food/application/scan2food/venv/lib/python3.12/site-packages/django/db/models/fields/__init__.py:1670: RuntimeWarning: DateTimeField Order.start_time received a naive datetime (2026-02-16 06:00:00) while time zone support is active.
Feb 15 05:48:37 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[216202]:   warnings.warn(
Feb 15 05:48:37 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[216202]: /var/www/scan2food/application/scan2food/venv/lib/python3.12/site-packages/gunicorn/workers/sync.py:190: Warning: StreamingHttpResponse must consume asynchronous iterators in order to serve them synchronously. Use a synchronous iterator instead.
Feb 15 05:48:37 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[216202]:   for item in respiter:        
Feb 15 05:53:30 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[216201]: /var/www/scan2food/application/scan2food/venv/lib/python3.12/site-packages/django/db/models/fields/__init__.py:1670: RuntimeWarning: DateTimeField Order.start_time received a naive datetime (2026-02-15 06:00:00) while time zone support is active.
Feb 15 05:53:30 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[216201]:   warnings.warn(
Feb 15 05:53:30 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[216201]: /var/www/scan2food/application/scan2food/venv/lib/python3.12/site-packages/django/db/models/fields/__init__.py:1670: RuntimeWarning: DateTimeField Order.start_time received a naive datetime (2026-02-16 06:00:00) while time zone support is active.
Feb 15 05:53:30 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[216201]:   warnings.warn(
Feb 15 05:53:30 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[216201]: /var/www/scan2food/application/scan2food/venv/lib/python3.12/site-packages/gunicorn/workers/sync.py:190: Warning: StreamingHttpResponse must consume asynchronous iterators in order to serve them synchronously. Use a synchronous iterator instead.
Feb 15 05:53:30 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[216201]:   for item in respiter:        
Feb 15 05:53:36 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[216201]: /var/www/scan2food/application/scan2food/venv/lib/python3.12/site-packages/django/db/models/fields/__init__.py:1670: RuntimeWarning: DateTimeField Order.start_time received a naive datetime (2026-02-09 06:00:00) while time zone support is active.
Feb 15 05:53:36 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[216201]:   warnings.warn(
Feb 16 09:56:47 ubuntu-s-1vcpu-1gb-amd-blr1-01 systemd[1]: Stopping gunicorn.service...
Feb 16 09:56:47 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[216201]: [2026-02-16 15:26:47 +0530] [216201] [INFO] Worker exiting (pid: 216201)
Feb 16 09:56:47 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[216202]: [2026-02-16 15:26:47 +0530] [216202] [INFO] Worker exiting (pid: 216202)
Feb 16 09:56:47 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[216199]: [2026-02-16 09:56:47 +0000] [216199] [INFO] Handling signal: term
Feb 16 09:56:49 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[216199]: [2026-02-16 09:56:49 +0000] [216199] [INFO] Shutting down: Master
Feb 16 09:56:49 ubuntu-s-1vcpu-1gb-amd-blr1-01 systemd[1]: gunicorn.service: Deactivated successfully.
Feb 16 09:56:49 ubuntu-s-1vcpu-1gb-amd-blr1-01 systemd[1]: Stopped gunicorn.service.
Feb 16 09:56:49 ubuntu-s-1vcpu-1gb-amd-blr1-01 systemd[1]: gunicorn.service: Consumed 32.060s CPU time.
Feb 16 09:56:49 ubuntu-s-1vcpu-1gb-amd-blr1-01 systemd[1]: Started gunicorn.service.
Feb 16 09:56:49 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[241716]: [2026-02-16 09:56:49 +0000] [241716] [INFO] Starting gunicorn 25.0.3
Feb 16 09:56:49 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[241716]: [2026-02-16 09:56:49 +0000] [241716] [INFO] Listening at: unix:/var/www/scan2food/application/scan2food/gunicorn.sock (241716) 
Feb 16 09:56:49 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[241716]: [2026-02-16 09:56:49 +0000] [241716] [INFO] Using worker: sync
Feb 16 09:56:49 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[241722]: [2026-02-16 09:56:49 +0000] [241722] [INFO] Booting worker with pid: 241722
Feb 16 09:56:49 ubuntu-s-1vcpu-1gb-amd-blr1-01 gunicorn[241723]: [2026-02-16 09:56:49 +0000] [241723] [INFO] Booting worker with pid: 241723
Feb 16 09:56:52 ubuntu-s-1vcpu-1gb-amd-blr1-01 systemd[1]: /etc/systemd/system/gunicorn.service:1: Assignment outside of section. Ignoring.
Feb 16 09:56:52 ubuntu-s-1vcpu-1gb-amd-blr1-01 systemd[1]: /etc/systemd/system/gunicorn.service:2: Assignment outside of section. Ignoring.
Feb 16 09:56:52 ubuntu-s-1vcpu-1gb-amd-blr1-01 systemd[1]: /etc/systemd/system/gunicorn.service:3: Assignment outside of section. Ignoring.
root@ubuntu-s-1vcpu-1gb-amd-blr1-01:/var/www/scan2food# cat /etc/systemd/system/gunicorn.service
kk[Unit]
Description=Gunicorn daemon
After=network.target

[Service]
User=root
Group=www-data

WorkingDirectory=/var/www/scan2food/application/scan2food

EnvironmentFile=/var/www/scan2food/application/scan2food/.env

ExecStart=/var/www/scan2food/application/scan2food/venv/bin/gunicorn --workers 2 --bind unix:/var/www/scan2food/application/scan2food/gunicorn.sock theatreApp.wsgi:application

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target

root@ubuntu-s-1vcpu-1gb-amd-blr1-01:/var/www/scan2food# sudo systemctl daemon-reload && sudo systemctl restart gunicorn && sudo systemctl restart daphne && sleep 3 && echo "Testing API (should return 401):" && curl https://scan2food.com/theatre/api/all-menu/1 | head -20
Testing API (should return 401):
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
{"commission": 5.9, "tax_type": "IGST", "all_category": [{"name": "Popcorn", "id": 3, "category_image": "http://scan2food.com/static/assets/images/category/Popcorn.png", "items": [{"item_id": 5, "name": "Cheese Popcorn Medium", "description": "-", "real_price": 100.0, "price": 105.9, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/chese-popcorn.png", "made_by": "in-house", "min_time": 5, "max_time": 30}, {"item_id": 3, "name": "Large Popcorn", "description": "-", "real_price": 1.0, "price": 1.06, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/pop-corn_qxDeJsw.jpg", "made_by": "in-house", "min_time": 5, "max_time": 30}, {"item_id": 4, "name": "Medium Popcorn", "description": "-", "real_price": 9443.0, "price": 10000.14, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/popcorn00_oTNAEAk.jpg", "made_by": "in-house", "min_time": 5, "max_time": 30}]}, {"name": "Pizza", "id": 61, "category_image": "http://scan2food.com/static/assets/images/category/Pizza.png", "items": [{"item_id": 37, "name": "Paneer Tikka Pizza", "description": "-", "real_price": 230.0, "price": 243.57, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/pizza_vWNnLrK.webp", "made_by": "in-house", "min_time": 5, "max_time": 30}]}, {"name": "Fast Food", "id": 5, "category_image": "http://scan2food.com/static/assets/images/category/Fast%20Food.png", "items": [{"item_id": 17, "name": "French fries", "description": "-", "real_price": 120.0, "price": 127.08, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/french-fries.jpg", "made_by": "in-house", "min_time": 5, "max_time": 30}, {"item_id": 18, "name": "Sweet Corn", "description": "-", "real_price": 80.0, "price": 84.72, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/sweet-corn.webp", "made_by": "in-house", "min_time": 5, "max_time": 30}, {"item_id": 19, "name": "Nachos (with Salsa & Mayo Dip)", "description": "-", "real_price": 140.0, "price": 148.26, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/nacho.jpg", "made_by": "in-house", "min_time": 5, "max_time": 30}, {"item_id": 20, "name": "Veg Aloo Patties", "description": "-", "real_price": 70.0, "price": 74.13, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/aloo-patties.webp", "made_by": "in-house", "min_time": 5, "max_time": 30}, {"item_id": 21, "name": "Veg Maggi", "description": "-", "real_price": 110.0, "price": 116.49, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/megi.jpeg", "made_by": "in-house", "min_time": 5, "max_time": 30}, {"item_id": 22, "name": "Cheese Maggi", "description": "-", "real_price": 130.0, "price": 137.67, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/megi_XaT6Ox8.jpeg", "made_by": "in-house", "min_time": 5, "max_time": 30}, {"item_id": 23, "name": "Veg Momos Fried (6 Pieces)", "description": "-", "real_price": 120.0, "price": 127.08, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/momos.webp", "made_by": "in-house", "min_time": 5, "max_time": 30}, {"item_id": 24, "name": "Paneer Momos Fried (4 Pieces)", "description": "-", "real_price": 140.0, "price": 148.26, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/momos_zFp0Y4L.webp", "made_by": "in-house", "min_time": 5, "max_time": 30}, {"item_id": 25, "name": "Corn & Cheese Momos Fried (6 Pieces)", "description": "-", "real_price": 140.0, "price": 148.26, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/momos_NtpWyd4.webp", "made_by": "in-house", "min_time": 5, "max_time": 30}, {"item_id": 26, "name": "Veg Cigar Roll (4 Pieces)", "description": "-", "real_price": 140.0, "price": 148.26, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/cigar-roll.webp", "made_by": "in-house", "min_time": 5, "max_time": 30}, {"item_id": 27, "name": "Paneer Cigar Roll (4 Pieces)", "description": "-", "real_price": 150.0, "price": 158.85, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/cigar-roll_MGYg15z.webp", "made_by": "in-house", "min_time": 5, "max_time": 30}]}, {"name": "Combos", "id": 13, "category_image": "http://scan2food.com/static/assets/images/category/Combos.png", "items": [{"item_id": 7, "name": "Medium Coke", "description": "-", "real_price": 130.0, "price": 137.67, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/coca-cola_ZMV3zcH.jpeg", "made_by": "in-house", "min_time": 5, "max_time": 30}, {"item_id": 169, "name": "test", "description": "__", "real_price": 1.0, "price": 1.06, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/sandwich_200_png_ALiaESf.png", "made_by": "in-house", "min_time": 5, "max_time": 30}]}, {"name": "Patty", "id": 6, "category_image": "http://scan2food.com/static/assets/images/category/Patty.png", "items": [{"item_id": 31, "name": "Veg Cheese Burger", "description": "-", "real_price": 120.0, "price": 127.08, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/burger.jpg", "made_by": "in-house", "min_time": 5, "max_time": 30}, {"item_id": 38, "name": "Veg Pasta (Red Sauce, White Sauce, Mix Sauce)", "description": "-", "real_price": 160.0, "price": 169.44, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/pasta.jpeg", "made_by": "in-house", "min_time": 5, "max_time": 30}, {"item_id": 34, "name": "Veg Club Sandwich", "description": "-", "real_price": 130.0, "price": 137.67, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/sandwich.jpg", "made_by": "in-house", "min_time": 5, "max_time": 30}, {"item_id": 32, "name": "Paneer Tikka Sandwich Grilled", "description": "-", "real_price": 150.0, "price": 158.85, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/sandwich_oZDrm5b.jpg", "made_by": "in-house", "min_time": 5, "max_time": 30}, {"item_id": 33, "name": "Veg Mexican Sandwich Grilled", "description": "-", "real_price": 140.0, "price": 148.26, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/sandwich_6C1quqM.jpg", "made_by": "in-house", "min_time": 5, "max_time": 30}, {"item_id": 36, "name": "Veg Mexican Pizza", "description": "-", "real_price": 190.0, "price": 201.21, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/pizza.webp", "made_by": "in-house", "min_time": 5, "max_time": 30}]}, {"name": "Dessert", "id": 60, "category_image": "http://scan2food.com/static/assets/images/category/Dessert.png", "items": [{"item_id": 9, "name": "Chocolate Shakes", "description": "-", "real_price": 130.0, "price": 137.67, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/oreo-shake.jpg", "made_by": "in-house", "min_time": 5, "max_time": 30}]}, {"name": "Beverages", "id": 4, "category_image": "http://scan2food.com/static/assets/images/category/Beverages.png", "items": [{"item_id": 16, "name": "Tea", "description": "-", "real_price": 70.0, "price": 74.13, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/tea.jpg", "made_by": "in-house", "min_time": 5, "max_time": 30}, {"item_id": 12, "name": "Cold Coffee With Ice Cream", "description": "-", "real_price": 140.0, "price": 148.26, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/download_4.jpg", "made_by": "packaged", "min_time": 5, "max_time": 30}, {"item_id": 13, "name": "Virgin Mojito Mocktail", "description": "-", "real_price": 120.0, "price": 127.08, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/mojito-mocktail.jpeg", "made_by": "in-house", "min_time": 5, "max_time": 30}, {"item_id": 6, "name": "Large Coke", "description": "-", "real_price": 150.0, "price": 158.85, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/coca-cola_JbjOqQo.jpeg", "made_by": "in-house", "min_time": 5, "max_time": 30}, {"item_id": 14, "name": "Ice Cream Cup", "description": "-", "real_price": 80.0, "price": 84.72, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/ice-100  8503  100  8503    0     0   151k      0 --:--:-- --:--:-- --:--:--  153k
cream.jpg", "made_by": "in-house", "min_time": 5, "max_time": 30}, {"item_id": 15, "name": "Hot Coffee", "description": "-", "real_price": 10.0, "price": 10.59, "food_type": "veg", "food_image": "http://scan2food.com/media/food_images/tea_JOjusiN.webp", "made_by": "in-house", "min_time": 5, "max_time": 30}]}]}root@ubuntu-s-1vcpu-1gb-amd-blr1-01:/var/www/scan2food#
# On the server
cd /var/www/scan2food
git pull origin 

RDnXh86Ciczn2Orbc2CxQtQ6VB-tzl19bcKTtNrSK4Y
```

#### Option B: Manual File Upload

Upload these files to the server:
- `application/scan2food/theatreApp/middleware.py` (NEW)
- `application/scan2food/theatreApp/settings.py` (MODIFIED)
- `application/scan2food/theatre/views.py` (MODIFIED)
- `application/scan2food/theatre/templates/theatre/show-menu.html` (MODIFIED)
- `application/scan2food/theatre/templates/theatre/show-new-menu.html` (MODIFIED)
- `static_files/scan2food-static/static/theatre_js/menu.js` (MODIFIED)
- `static_files/scan2food-static/static/theatre_js/new-menu.js` (MODIFIED)
- `static_files/scan2food-static/static/theatre_js/cart.js` (MODIFIED)

### Step 4: Restart Services

```bash
# Restart Gunicorn (Django application)
sudo systemctl restart gunicorn

# Restart Daphne (WebSocket server)
sudo systemctl restart daphne

# Restart Nginx (if needed)
sudo systemctl restart nginx
```

### Step 5: Verify Deployment

#### Test 1: Check Services Are Running
```bash
sudo systemctl status gunicorn
sudo systemctl status daphne
sudo systemctl status nginx
```

All should show "active (running)" in green.

#### Test 2: Test API Without Key (Should Fail)
```bash
curl https://scan2food.com/theatre/api/all-menu/1
```

Expected response:
```json
{"error": "Invalid or missing API key", "status": 401}
```

#### Test 3: Test API With Key (Should Work)
```bash
curl -H "X-API-Key: YOUR_API_KEY_HERE" https://scan2food.com/theatre/api/all-menu/1
```

Expected: Menu data returned successfully

#### Test 4: Test Customer Order Flow
1. Scan a QR code from a theatre
2. Menu should load normally
3. Add items to cart
4. Create order
5. Verify order is created successfully

#### Test 5: Test Webhook (Should Work Without API Key)
Webhooks should continue to work normally without API keys.

### Step 6: Monitor Logs

Watch for failed authentication attempts:
```bash
# View Django logs
tail -f /var/log/gunicorn/error.log

# Look for lines like:
# WARNING api_security: API key validation failed - IP: 1.2.3.4, Path: /theatre/api/all-menu/1
```

## Security Monitoring

### Check Failed Authentication Attempts

```bash
# View recent failed attempts
grep "API key validation failed" /var/log/gunicorn/error.log | tail -20
```

### Identify Suspicious Activity

Look for:
- Multiple failed attempts from same IP
- Attempts to access many different endpoints
- Unusual access patterns

## API Key Rotation

### When to Rotate:
- Every 3-6 months (routine)
- Immediately if key is compromised
- When suspicious activity is detected
- When staff with key access leaves

### How to Rotate:

1. Generate new key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. Update `.env` file with new key

3. Restart services:
```bash
sudo systemctl restart gunicorn
sudo systemctl restart daphne
```

4. Test immediately to ensure customers can still order

**Note**: Rotation is instant - old key stops working immediately after restart.

## Troubleshooting

### Problem: Customers Can't Load Menu

**Symptoms**: Menu page loads but shows no items

**Solution**:
1. Check browser console for errors (F12)
2. Look for "401 Unauthorized" errors
3. Verify API key is set in `.env`
4. Verify services were restarted after adding key

### Problem: "API_KEY not configured" Error

**Symptoms**: Server won't start, shows error about missing API_KEY

**Solution**:
1. Ensure `.env` file exists in `application/scan2food/`
2. Ensure `API_KEY=...` line is present
3. Restart services

### Problem: Webhooks Not Working

**Symptoms**: Payments not updating, webhook errors in payment gateway dashboard

**Solution**:
1. Webhooks should NOT require API key
2. Check middleware is excluding webhook URLs
3. Verify webhook URLs contain "webhook" in the path
4. Check payment gateway logs

### Problem: Theatre Staff Can't Access Dashboard

**Symptoms**: Staff getting 401 errors on dashboard

**Solution**:
1. Ensure staff are logged in (check session)
2. Middleware should skip authenticated users
3. Check Django authentication is working

## Rollback Procedure

If something goes wrong and you need to rollback:

### Quick Rollback (Disable Middleware):

1. Edit `settings.py`:
```bash
nano application/scan2food/theatreApp/settings.py
```

2. Comment out the middleware line:
```python
MIDDLEWARE = [
    # ... other middleware ...
    # 'theatreApp.middleware.APIKeyMiddleware',  # DISABLED
]
```

3. Restart services:
```bash
sudo systemctl restart gunicorn
sudo systemctl restart daphne
```

### Full Rollback (Revert Code):

```bash
cd /var/www/scan2food
git revert HEAD
sudo systemctl restart gunicorn
sudo systemctl restart daphne
```

## Production Checklist

Before going live, verify:

- [ ] API key generated and stored securely
- [ ] `.env` file updated with API key
- [ ] All code files deployed to server
- [ ] Services restarted successfully
- [ ] Test: API without key returns 401
- [ ] Test: Customer can load menu and order
- [ ] Test: Webhooks still working
- [ ] Test: Theatre staff can access dashboard
- [ ] Monitoring logs for errors
- [ ] Backup of old code taken

## Security Best Practices

1. **Never commit API keys to git**
   - Always use environment variables
   - Add `.env` to `.gitignore`

2. **Rotate keys regularly**
   - Set calendar reminder for every 3 months
   - Document rotation in security log

3. **Monitor failed attempts**
   - Check logs weekly
   - Investigate unusual patterns

4. **Limit key exposure**
   - Only share with necessary staff
   - Use different keys for dev/production

5. **Have rollback plan ready**
   - Keep backup of working code
   - Document rollback steps

## Support

If you encounter issues:

1. Check logs: `/var/log/gunicorn/error.log`
2. Verify services are running: `sudo systemctl status gunicorn`
3. Test API endpoints manually with curl
4. Check browser console for JavaScript errors

## Summary

You've successfully implemented API key authentication that:
- ✅ Protects customer-facing endpoints from unauthorized access
- ✅ Blocks old developer from accessing APIs
- ✅ Maintains webhook functionality
- ✅ Doesn't affect theatre staff operations
- ✅ Provides security logging
- ✅ Allows easy key rotation

The old developer can no longer access your endpoints without the new API key!
