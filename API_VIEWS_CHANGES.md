# Changes to api_views.py

## Step 1: Add Import at Top

Find the imports section at the top of `application/scan2food/theatre/api_views.py` and add:

```python
# Add this import with other imports
from .webhook_security import verify_webhook_request
```

---

## Step 2: Update razporpay_webhook_url Function

Find the function `razporpay_webhook_url` (around line 936) and replace it with:

```python
@csrf_exempt
@api_view(['GET', 'POST'])
def razporpay_webhook_url(request):
    """Razorpay Webhook Handler with Signature Verification"""
    if request.method == 'POST':
        
        # STEP 1: Verify webhook signature FIRST
        is_valid, error_message = verify_webhook_request(request, 'Razorpay')
        
        if not is_valid:
            print(f"❌ Razorpay webhook signature verification failed: {error_message}")
            return JsonResponse(
                {'status': 'error', 'message': 'Invalid signature'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        print("✅ Razorpay webhook signature verified")
        
        # STEP 2: Process the webhook payload (existing code below)
        request_data = request.data
        
        # ... rest of your existing code stays the same ...
```

**Key Changes:**
1. Added signature verification at the start
2. Return 401 error if signature is invalid
3. Only process payment if signature is valid
4. Added logging for debugging

---

## Step 3: Update split_razporpay_webhook_url Function

Find the function `split_razporpay_webhook_url` (around line 1020) and replace it with:

```python
@csrf_exempt
@api_view(['GET', 'POST'])
def split_razporpay_webhook_url(request):
    """Split Razorpay Webhook Handler with Signature Verification"""
    if request.method == 'POST':
        
        # STEP 1: Verify webhook signature FIRST
        is_valid, error_message = verify_webhook_request(request, 'split_razorpay')
        
        if not is_valid:
            print(f"❌ Split Razorpay webhook signature verification failed: {error_message}")
            return JsonResponse(
                {'status': 'error', 'message': 'Invalid signature'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        print("✅ Split Razorpay webhook signature verified")
        
        # STEP 2: Process the webhook payload (existing code below)
        request_data = request.data
        
        # ... rest of your existing code stays the same ...
```

**Key Changes:**
1. Added signature verification at the start
2. Return 401 error if signature is invalid
3. Only process payment if signature is valid
4. Added logging for debugging

---

## Complete Example

Here's what the updated function looks like:

```python
@csrf_exempt
@api_view(['GET', 'POST'])
def razporpay_webhook_url(request):
    """Razorpay Webhook Handler with Signature Verification"""
    if request.method == 'POST':
        
        # ========== NEW CODE: Signature Verification ==========
        is_valid, error_message = verify_webhook_request(request, 'Razorpay')
        
        if not is_valid:
            print(f"❌ Razorpay webhook signature verification failed: {error_message}")
            return JsonResponse(
                {'status': 'error', 'message': 'Invalid signature'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        print("✅ Razorpay webhook signature verified")
        # ========== END NEW CODE ==========

        # ========== EXISTING CODE (unchanged) ==========
        request_data = request.data
        
        # get payment gateway from database
        gateway_detail = PaymentGateway.objects.get(name='Razorpay')
        client = razorpay.Client(auth=(gateway_detail.gateway_key, gateway_detail.gateway_secret))
        try:
            payment_id = request_data['payload']['payment']['entity']['id']
            order_id = request_data['payload']['payment']['entity']['order_id']
            razorpay_payment = RazorpayPayment.objects.get(razorpay_order_id=order_id)

            payment_status = request_data['payload']['payment']['entity']['status']
            if payment_status == 'captured':
                # ... rest of existing code ...
                
        except razorpay.errors.SignatureVerificationError:
            # ... existing error handling ...
            
    return JsonResponse({'status': 'success'}, status=status.HTTP_200_OK)
```

---

## What This Does

1. **Before processing payment:**
   - Extracts signature from request header
   - Gets webhook secret from .env
   - Verifies signature using HMAC-SHA256
   - Rejects if signature is invalid

2. **If signature is valid:**
   - Proceeds with existing payment processing
   - Updates order status
   - Sends WebSocket update
   - Everything works as before

3. **If signature is invalid:**
   - Returns 401 Unauthorized
   - Logs error message
   - Does NOT process payment
   - Protects against fake webhooks

---

## Testing After Changes

### Test 1: Real Payment
```bash
# Monitor logs
sudo journalctl -u gunicorn -f

# Create order and pay
# You should see:
✅ Razorpay webhook signature verified
✅ Payment processed successfully: Order XXXXX
```

### Test 2: Fake Webhook
```bash
# Try to fake webhook with Postman
# You should see:
❌ Razorpay webhook signature verification failed: Missing X-Razorpay-Signature header
```

---

## Important Notes

1. **Don't remove existing code** - Only add the signature verification at the start
2. **Keep error handling** - The existing try/except blocks stay the same
3. **Test thoroughly** - Test with real payment before deploying
4. **Monitor logs** - Check Gunicorn logs for verification messages

---

## Rollback Plan

If something goes wrong, you can temporarily disable verification:

In `webhook_security.py`, change:
```python
if not webhook_secret:
    return True, None  # Allow for backward compatibility
```

This will log warnings but still process webhooks.

Then fix the issue and re-enable verification.

---

## Summary

**Changes:**
- ✅ Add 1 import
- ✅ Add 8 lines to each webhook function
- ✅ No changes to existing logic
- ✅ Backward compatible

**Result:**
- 🔒 Secure webhook verification
- 🛡️ Protection against fake payments
- 📝 Detailed logging
- ✅ Production-ready security
