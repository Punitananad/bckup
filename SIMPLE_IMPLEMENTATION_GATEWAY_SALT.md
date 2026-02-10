# Simple Implementation - Using gateway_salt (NO .env needed!)

## What Changed

✅ **Use existing `gateway_salt` field** (no new column)  
✅ **No .env file needed** (everything in database)  
✅ **Strict security** (wrong secret = payment fails)  

---

## Step 1: Pull Code

```bash
cd /var/www/scan2food
git pull origin main
```

---

## Step 2: Get Razorpay Webhook Secrets

1. Go to: https://dashboard.razorpay.com/
2. Settings → Webhooks
3. Copy webhook secret for Razorpay (starts with `whsec_`)
4. Copy webhook secret for Split Razorpay

---

## Step 3: Add Secrets to Database (Admin Panel)

### Option A: Via Admin Panel (Recommended)

1. Go to: `https://calculatentrade.com/admin/`
2. Navigate to: **AdminPortal → Payment gateways**
3. Click on **Razorpay**:
   - **Gateway salt**: Paste Razorpay webhook secret
   - Save
4. Click on **split_razorpay**:
   - **Gateway salt**: Paste Split Razorpay webhook secret
   - Save

### Option B: Via Django Shell

```bash
cd /var/www/scan2food/application/scan2food
source venv/bin/activate
python manage.py shell
```

```python
from adminPortal.models import PaymentGateway

# Update Razorpay
razorpay = PaymentGateway.objects.get(name='Razorpay')
razorpay.gateway_salt = 'whsec_your_razorpay_webhook_secret'
razorpay.save()

# Update Split Razorpay
split = PaymentGateway.objects.get(name='split_razorpay')
split.gateway_salt = 'whsec_your_split_webhook_secret'
split.save()

exit()
```

---

## Step 4: Update api_views.py

```bash
cd /var/www/scan2food/application/scan2food
nano theatre/api_views.py
```

### Add Import at Top:

```python
from .webhook_security import verify_webhook_request
```

### Update razporpay_webhook_url (around line 936):

```python
@csrf_exempt
@api_view(['GET', 'POST'])
def razporpay_webhook_url(request):
    if request.method == 'POST':
        
        # ADD THIS: Get gateway and verify
        gateway_detail = PaymentGateway.objects.get(name='Razorpay')
        is_valid, error_message = verify_webhook_request(request, 'Razorpay', gateway_detail.gateway_salt)
        
        if not is_valid:
            print(f"❌ Razorpay webhook verification failed: {error_message}")
            return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=401)
        
        print("✅ Razorpay webhook verified")
        
        # ... rest of existing code stays the same ...
```

### Update split_razporpay_webhook_url (around line 1020):

```python
@csrf_exempt
@api_view(['GET', 'POST'])
def split_razporpay_webhook_url(request):
    if request.method == 'POST':
        
        # ADD THIS: Get gateway and verify
        gateway_detail = PaymentGateway.objects.get(name='split_razorpay')
        is_valid, error_message = verify_webhook_request(request, 'split_razorpay', gateway_detail.gateway_salt)
        
        if not is_valid:
            print(f"❌ Split Razorpay webhook verification failed: {error_message}")
            return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=401)
        
        print("✅ Split Razorpay webhook verified")
        
        # ... rest of existing code stays the same ...
```

Save: `Ctrl+X`, `Y`, `Enter`

---

## Step 5: Restart Services

```bash
sudo systemctl restart gunicorn daphne
sleep 10
sudo systemctl status gunicorn daphne
```

---

## Step 6: Test

### Monitor Logs:

```bash
sudo journalctl -u gunicorn -f
```

### Test Scenarios:

#### ✅ Correct Secret:
- Create order → Pay → Should work
- Logs: `✅ Razorpay webhook verified`

#### ❌ Wrong Secret:
- Change gateway_salt to wrong value
- Create order → Pay → Should FAIL
- Logs: `❌ Razorpay webhook verification failed: Invalid webhook signature`

#### ❌ No Secret:
- Clear gateway_salt field
- Create order → Pay → Should FAIL
- Logs: `❌ ERROR: No webhook secret configured`

---

## What Happens with Wrong Secret

```
Customer pays → Razorpay sends webhook → Your server verifies signature
→ Signature mismatch → Return 401 error → Payment NOT confirmed
→ Order stays pending → Customer doesn't get confirmation
```

**This is EXACTLY what you want!** It prevents fake payments.

---

## Quick Commands (All in One)

```bash
# Pull code
cd /var/www/scan2food && git pull origin main

# Update api_views.py (manual step - see above)

# Restart
cd application/scan2food && sudo systemctl restart gunicorn daphne

# Test
sleep 10 && sudo journalctl -u gunicorn -f
```

---

## Summary

✅ **No .env file needed**  
✅ **Use existing gateway_salt field**  
✅ **Strict security** (wrong secret = fail)  
✅ **Simple to manage** (via admin panel)  
✅ **No database migration needed**  

Just:
1. Pull code
2. Add webhook secrets to admin panel
3. Update api_views.py
4. Restart services
5. Test!

---

## Files to Check

- **SECURE_WEBHOOKS_USE_GATEWAY_SALT.py** - Code examples
- **webhook_security.py** - Verification logic (already updated)
- **models.py** - gateway_salt field (already updated)
