# Server Setup Commands - Copy & Paste

## Step 1: Pull the Code

```bash
cd /var/www/scan2food
git pull origin main
```

---

## Step 2: Get Razorpay Webhook Secrets

1. Go to: https://dashboard.razorpay.com/
2. Click: **Settings** → **Webhooks**
3. Find webhook with URL: `/theatre/api/razorpay-webhook-url`
   - Click on it
   - Copy the **Webhook Secret** (starts with `whsec_`)
4. Find webhook with URL: `/theatre/api/split-razorpay-webhook-url`
   - Click on it
   - Copy the **Webhook Secret**

---

## Step 3: Add Secrets to .env

```bash
cd /var/www/scan2food/application/scan2food
nano .env
```

Add these lines at the end:

```bash
# Razorpay Webhook Secrets
RAZORPAY_WEBHOOK_SECRET=whsec_paste_your_razorpay_secret_here
SPLIT_RAZORPAY_WEBHOOK_SECRET=whsec_paste_your_split_secret_here
```

Save: `Ctrl+X`, then `Y`, then `Enter`

---

## Step 4: Install python-dotenv

```bash
cd /var/www/scan2food/application/scan2food
source venv/bin/activate
pip install python-dotenv
```

---

## Step 5: Update settings.py

```bash
nano theatreApp/settings.py
```

Add these lines at the **very top** (after the docstring, before other imports):

```python
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
```

Save: `Ctrl+X`, then `Y`, then `Enter`

---

## Step 6: Run Migration

```bash
cd /var/www/scan2food/application/scan2food
source venv/bin/activate
python manage.py makemigrations
python manage.py migrate
```

---

## Step 7: Update api_views.py

```bash
nano theatre/api_views.py
```

### 7.1 Add Import at Top

Find the imports section and add:

```python
from .webhook_security import (
    verify_webhook_request,
    verify_payu_webhook,
    verify_phonepe_webhook,
    validate_ccavenue_webhook
)
```

### 7.2 Update Razorpay Webhook (around line 936)

Find `def razporpay_webhook_url(request):` and add this at the start of the function:

```python
@csrf_exempt
@api_view(['GET', 'POST'])
def razporpay_webhook_url(request):
    if request.method == 'POST':
        
        # ADD THIS: Verify signature FIRST
        is_valid, error_message = verify_webhook_request(request, 'Razorpay')
        if not is_valid:
            print(f"❌ Razorpay webhook verification failed: {error_message}")
            return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=401)
        print("✅ Razorpay webhook verified")
        
        # ... rest of existing code stays the same ...
```

### 7.3 Update Split Razorpay Webhook (around line 1020)

Find `def split_razporpay_webhook_url(request):` and add this at the start:

```python
@csrf_exempt
@api_view(['GET', 'POST'])
def split_razporpay_webhook_url(request):
    if request.method == 'POST':
        
        # ADD THIS: Verify signature FIRST
        is_valid, error_message = verify_webhook_request(request, 'split_razorpay')
        if not is_valid:
            print(f"❌ Split Razorpay webhook verification failed: {error_message}")
            return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=401)
        print("✅ Split Razorpay webhook verified")
        
        # ... rest of existing code stays the same ...
```

Save: `Ctrl+X`, then `Y`, then `Enter`

---

## Step 8: Restart Services

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

## Step 9: Test

### Monitor Logs:

```bash
sudo journalctl -u gunicorn -f
```

### Create Test Order:

1. Go to your website
2. Create an order
3. Complete payment
4. Check logs - you should see:
   ```
   ✅ Razorpay webhook verified
   ✅ Payment processed successfully
   ```

---

## Quick Commands (All in One)

```bash
# Pull code
cd /var/www/scan2food && git pull origin main

# Install dotenv
cd application/scan2food && source venv/bin/activate && pip install python-dotenv

# Run migration
python manage.py makemigrations && python manage.py migrate

# Restart services
sudo systemctl restart gunicorn daphne

# Check status
sleep 10 && sudo systemctl status gunicorn daphne
```

---

## What to Do Next

1. ✅ Pull code (done above)
2. ⏳ Get Razorpay webhook secrets from dashboard
3. ⏳ Add secrets to .env file
4. ⏳ Update settings.py (add load_dotenv)
5. ⏳ Run migration
6. ⏳ Update api_views.py (add verification)
7. ⏳ Restart services
8. ⏳ Test with real payment

---

## Need Help?

**Detailed Guide:** IMPLEMENT_ALL_GATEWAYS_SECURITY.md  
**Code Examples:** ALL_SECURE_WEBHOOK_VIEWS.py  
**Check Logs:** `sudo journalctl -u gunicorn -f`

---

## Summary

✅ Code pushed to GitHub  
⏳ Follow steps above on server  
⏳ Test with real payment  
✅ All gateways will be secure!
