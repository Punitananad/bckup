# Exact Code Changes for api_views.py

## Step 1: Add Import

Find this line (around line 17):
```python
from .update_websocket import update_websocket, send_invoice
```

Add this line RIGHT AFTER it:
```python
from .webhook_security import verify_webhook_request
```

---

## Step 2: Update razporpay_webhook_url

Find this function (around line 936):
```python
@csrf_exempt
@api_view(['GET', 'POST'])
def razporpay_webhook_url(request):
    if request.method == 'POST':

        request_data = request.data
        
        # get payment gateway from database
        gateway_detail = PaymentGateway.objects.get(name='Razorpay')
```

**REPLACE WITH:**
```python
@csrf_exempt
@api_view(['GET', 'POST'])
def razporpay_webhook_url(request):
    if request.method == 'POST':
        
        # get payment gateway from database
        gateway_detail = PaymentGateway.objects.get(name='Razorpay')
        
        # VERIFY WEBHOOK SIGNATURE FIRST
        is_valid, error_message = verify_webhook_request(request, 'Razorpay', gateway_detail.gateway_salt)
        if not is_valid:
            print(f"❌ Razorpay webhook verification failed: {error_message}")
            return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=401)
        print("✅ Razorpay webhook verified")

        request_data = request.data
```

---

## Step 3: Update split_razporpay_webhook_url

Find this function (around line 1020):
```python
@csrf_exempt
@api_view(['GET', 'POST'])
def split_razporpay_webhook_url(request):
    if request.method == 'POST':

        request_data = request.data
        
        # get payment gateway from database
        gateway_detail = PaymentGateway.objects.get(name='split_razorpay')
```

**REPLACE WITH:**
```python
@csrf_exempt
@api_view(['GET', 'POST'])
def split_razporpay_webhook_url(request):
    if request.method == 'POST':
        
        # get payment gateway from database
        gateway_detail = PaymentGateway.objects.get(name='split_razorpay')
        
        # VERIFY WEBHOOK SIGNATURE FIRST
        is_valid, error_message = verify_webhook_request(request, 'split_razorpay', gateway_detail.gateway_salt)
        if not is_valid:
            print(f"❌ Split Razorpay webhook verification failed: {error_message}")
            return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=401)
        print("✅ Split Razorpay webhook verified")

        request_data = request.data
```

---

## Commands to Run:

```bash
# 1. Edit the file
nano theatre/api_views.py

# 2. Make the 3 changes above

# 3. Save: Ctrl+X, Y, Enter

# 4. Restart services
sudo systemctl restart gunicorn daphne
```

---

## What This Does:

1. **Imports verification function**
2. **Gets gateway_salt from database** (webhook secret)
3. **Verifies signature BEFORE processing payment**
4. **If wrong secret → Returns 401 error** (payment fails)
5. **If correct secret → Processes payment** (payment succeeds)

---

## Testing:

```bash
# Monitor logs
sudo journalctl -u gunicorn -f

# Create test order and pay
# Should see: ✅ Razorpay webhook verified
```
