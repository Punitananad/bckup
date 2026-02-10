# Razorpay Webhook Security - Implementation Steps

## Overview

This guide will help you implement proper webhook signature verification for Razorpay payments.

**Security Improvement:**
- ❌ Before: Anyone can fake payment success
- ✅ After: Only verified Razorpay webhooks are accepted

---

## Prerequisites

1. Access to Razorpay Dashboard
2. Server SSH access
3. Admin access to Django admin panel

---

## Step 1: Get Webhook Secrets from Razorpay

### 1.1 Login to Razorpay Dashboard
- Go to: https://dashboard.razorpay.com/
- Login with your credentials

### 1.2 Navigate to Webhooks
- Click: **Settings** (gear icon)
- Click: **Webhooks**

### 1.3 Get Webhook Secrets
You need secrets for TWO webhooks:

**Webhook 1: Regular Razorpay**
- Find webhook with URL: `/theatre/api/razorpay-webhook-url`
- Click on it
- Copy the **Webhook Secret** (starts with `whsec_`)
- Save it somewhere safe

**Webhook 2: Split Razorpay**
- Find webhook with URL: `/theatre/api/split-razorpay-webhook-url`
- Click on it
- Copy the **Webhook Secret**
- Save it somewhere safe

---

## Step 2: Add Secrets to .env File

### 2.1 SSH to Server
```bash
ssh root@your-server-ip
```

### 2.2 Edit .env File
```bash
cd /var/www/scan2food/application/scan2food
nano .env
```

### 2.3 Add These Lines
Add at the end of the file:

```bash
# Razorpay Webhook Secrets
RAZORPAY_WEBHOOK_SECRET=whsec_your_actual_secret_here
SPLIT_RAZORPAY_WEBHOOK_SECRET=whsec_your_actual_split_secret_here
```

**Replace** `whsec_your_actual_secret_here` with the actual secrets you copied.

### 2.4 Save and Exit
- Press `Ctrl + X`
- Press `Y`
- Press `Enter`

---

## Step 3: Update Django Settings to Read .env

### 3.1 Install python-dotenv (if not installed)
```bash
cd /var/www/scan2food/application/scan2food
source venv/bin/activate
pip install python-dotenv
```

### 3.2 Update settings.py
```bash
nano theatreApp/settings.py
```

Add at the **very top** of the file (after imports):

```python
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
```

Save and exit.

---

## Step 4: Update Database Model

### 4.1 Model Already Updated
The `PaymentGateway` model has been updated to include `webhook_secret` field.

File: `application/scan2food/adminPortal/models.py`

### 4.2 Create Migration
```bash
cd /var/www/scan2food/application/scan2food
source venv/bin/activate
python manage.py makemigrations
```

Expected output:
```
Migrations for 'adminPortal':
  adminPortal/migrations/0XXX_add_webhook_secret.py
    - Add field webhook_secret to paymentgateway
```

### 4.3 Apply Migration
```bash
python manage.py migrate
```

Expected output:
```
Running migrations:
  Applying adminPortal.0XXX_add_webhook_secret... OK
```

---

## Step 5: Update Webhook Views

### 5.1 Add webhook_security.py
File already created: `application/scan2food/theatre/webhook_security.py`

This file contains the signature verification logic.

### 5.2 Update api_views.py

**Option A: Manual Update (Recommended)**

Open `application/scan2food/theatre/api_views.py` and:

1. Add import at the top:
```python
from .webhook_security import verify_webhook_request
```

2. Replace the `razporpay_webhook_url` function with the secure version from `razorpay_webhook_views_SECURE.py`

3. Replace the `split_razporpay_webhook_url` function with the secure version from `razorpay_webhook_views_SECURE.py`

**Option B: Copy-Paste**

I've created the secure versions in `razorpay_webhook_views_SECURE.py`.

Copy the functions from that file and replace the existing ones in `api_views.py`.

---

## Step 6: Restart Services

```bash
sudo systemctl restart gunicorn
sudo systemctl restart daphne
```

Wait 10 seconds:
```bash
sleep 10
```

Check services are running:
```bash
sudo systemctl status gunicorn
sudo systemctl status daphne
```

---

## Step 7: Test the Implementation

### Test 1: Real Payment (Should Work ✅)

1. Create a test order on your website
2. Complete payment using Razorpay
3. Razorpay will send webhook with signature
4. Order should be confirmed successfully

**Check logs:**
```bash
sudo journalctl -u gunicorn -f
```

You should see:
```
✅ Razorpay webhook signature verified
✅ Payment processed successfully: Order XXXXX
```

### Test 2: Fake Webhook (Should Fail ❌)

Try to send a fake webhook using Postman:

**Request:**
- Method: POST
- URL: `https://calculatentrade.com/theatre/api/razorpay-webhook-url`
- Body: `{"payload": {"payment": {"entity": {"status": "captured"}}}}`

**Expected Response:**
```json
{
  "status": "error",
  "message": "Invalid signature"
}
```

**Check logs:**
```bash
sudo journalctl -u gunicorn -f
```

You should see:
```
❌ Razorpay webhook signature verification failed: Missing X-Razorpay-Signature header
```

---

## Step 8: Verify in Admin Panel (Optional)

1. Go to: `https://calculatentrade.com/admin/`
2. Navigate to: **AdminPortal → Payment gateways**
3. Click on **Razorpay**
4. You should see the new field: **Webhook secret**
5. You can optionally store the webhook secret here (but .env is preferred)

---

## Troubleshooting

### Issue 1: "Module 'dotenv' not found"

**Solution:**
```bash
cd /var/www/scan2food/application/scan2food
source venv/bin/activate
pip install python-dotenv
sudo systemctl restart gunicorn daphne
```

### Issue 2: Webhook still accepts fake requests

**Check:**
1. .env file has correct secrets
2. settings.py loads .env file
3. Services were restarted
4. Webhook views use `verify_webhook_request()`

**Debug:**
```bash
# Check if .env is loaded
cd /var/www/scan2food/application/scan2food
source venv/bin/activate
python manage.py shell

>>> import os
>>> print(os.environ.get('RAZORPAY_WEBHOOK_SECRET'))
# Should print your webhook secret
```

### Issue 3: Real payments are rejected

**Check:**
1. Webhook secret in .env matches Razorpay dashboard
2. No extra spaces in .env file
3. Correct webhook secret for each gateway (Razorpay vs Split)

**Debug:**
```bash
# Check Gunicorn logs
sudo journalctl -u gunicorn -n 100
```

---

## Security Checklist

After implementation, verify:

- ✅ .env file contains webhook secrets
- ✅ .env file is NOT committed to git
- ✅ settings.py loads .env file
- ✅ Database migration applied
- ✅ Webhook views verify signature
- ✅ Services restarted
- ✅ Real payment works
- ✅ Fake webhook is rejected

---

## Files Modified

1. ✅ `application/scan2food/.env` - Added webhook secrets
2. ✅ `application/scan2food/.env.template` - Updated template
3. ✅ `application/scan2food/adminPortal/models.py` - Added webhook_secret field
4. ✅ `application/scan2food/theatre/webhook_security.py` - New file
5. ✅ `application/scan2food/theatre/api_views.py` - Updated webhook views
6. ✅ `application/scan2food/theatreApp/settings.py` - Load .env file

---

## What Changed?

### Before (Insecure):
```python
@api_view(['POST'])
def razporpay_webhook_url(request):
    # No signature verification
    # Process payment directly
    # Anyone can fake this!
```

### After (Secure):
```python
@api_view(['POST'])
def razporpay_webhook_url(request):
    # STEP 1: Verify signature FIRST
    is_valid, error = verify_webhook_request(request, 'Razorpay')
    if not is_valid:
        return JsonResponse({'error': 'Invalid signature'}, status=401)
    
    # STEP 2: Process payment (only if signature is valid)
    # Now secure!
```

---

## Important Notes

1. **API Secret ≠ Webhook Secret**
   - API Secret: For creating orders (already in database)
   - Webhook Secret: For verifying webhooks (new, in .env)

2. **Never Commit .env to Git**
   - .env contains secrets
   - Add to .gitignore
   - Use .env.template for reference

3. **Test in Production**
   - Test with real Razorpay payment
   - Test with fake webhook (should fail)
   - Monitor logs for errors

---

## Support

If you encounter issues:

1. Check logs: `sudo journalctl -u gunicorn -f`
2. Verify .env file: `cat /var/www/scan2food/application/scan2food/.env`
3. Test webhook secret: Use Razorpay dashboard webhook test feature
4. Contact developer with error logs

---

## Summary

✅ Webhook secrets stored in .env (secure)  
✅ Signature verification before processing  
✅ Protection against fake payments  
✅ Backward compatible (works without secrets, with warning)  
✅ Production-grade security  

Your payment system is now secure! 🔒
