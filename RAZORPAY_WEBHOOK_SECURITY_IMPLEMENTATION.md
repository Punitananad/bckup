# Razorpay Webhook Security Implementation

## Problem

❌ **Current Setup:** No webhook signature verification  
❌ **Risk:** Anyone can fake payment success by calling your webhook  
✅ **Solution:** Add webhook secret verification  

---

## What We're Doing

1. **Remove:** `gateway_salt` field (not used for Razorpay)
2. **Add:** `webhook_secret` field to PaymentGateway model
3. **Store:** Webhook secret in `.env` file
4. **Verify:** Webhook signature before processing payment

---

## Step-by-Step Implementation

### Step 1: Update .env File

Add Razorpay webhook secrets to `.env`:

```bash
# Razorpay Webhook Secrets
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret_here
SPLIT_RAZORPAY_WEBHOOK_SECRET=your_split_webhook_secret_here
```

**How to get webhook secret:**
1. Go to Razorpay Dashboard
2. Settings → Webhooks
3. Create/Edit webhook
4. Copy the "Webhook Secret"

---

### Step 2: Update PaymentGateway Model

**File:** `application/scan2food/adminPortal/models.py`

Change from:
```python
gateway_salt = models.CharField(max_length=100, null=True, blank=True)
```

To:
```python
webhook_secret = models.CharField(max_length=200, null=True, blank=True)
```

---

### Step 3: Create Migration

```bash
cd /var/www/scan2food/application/scan2food
source venv/bin/activate
python manage.py makemigrations
python manage.py migrate
```

---

### Step 4: Update Webhook Views

**File:** `application/scan2food/theatre/api_views.py`

Add proper signature verification.

---

### Step 5: Update Django Settings

**File:** `application/scan2food/theatreApp/settings.py`

Add code to read from .env file.

---

## Security Benefits

### Before (Insecure):
```
Attacker → POST /webhook {"status": "paid"} → ✅ Accepted
Anyone can fake payments!
```

### After (Secure):
```
Razorpay → POST /webhook + Signature → Verify → ✅ Accepted
Attacker → POST /webhook + No/Wrong Signature → ❌ Rejected
```

---

## Important Notes

1. **API Secret ≠ Webhook Secret**
   - API Secret: Used for creating orders
   - Webhook Secret: Used for verifying webhooks

2. **Never expose webhook secret in frontend**
   - Keep it in `.env` file only
   - Never commit to git

3. **Verify signature BEFORE processing payment**
   - Check signature first
   - Then update database

---

## Files to Modify

1. ✅ `.env` - Add webhook secrets
2. ✅ `adminPortal/models.py` - Rename gateway_salt to webhook_secret
3. ✅ `theatre/api_views.py` - Add signature verification
4. ✅ `theatreApp/settings.py` - Read from .env
5. ✅ Run migrations

---

## Testing

After implementation:

1. **Test with real Razorpay webhook:**
   - Create test order
   - Razorpay sends webhook
   - Should work ✅

2. **Test with fake webhook (Postman):**
   - Send POST to webhook URL
   - Should be rejected ❌

---

## Next Steps

I'll create the code changes for you. You'll need to:

1. Add webhook secrets to `.env` file
2. Apply the code changes
3. Run migrations
4. Restart services
5. Test with real payment

Ready to proceed?
