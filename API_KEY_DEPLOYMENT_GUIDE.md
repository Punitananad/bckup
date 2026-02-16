# API Key Security Deployment Guide

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

# On the server
cd /var/www/scan2food
git pull origin main
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
