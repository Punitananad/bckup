"""
SECURE Webhook Views - Using gateway_salt field (NO .env needed)
Replace the existing webhook views in api_views.py with these
"""

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse, HttpResponse
from django.utils.timezone import localtime
from django.utils import timezone
from django.urls import reverse
import razorpay

from adminPortal.models import PaymentGateway
from .update_websocket import update_websocket
from .webhook_security import verify_webhook_request


# ============================================================================
# RAZORPAY WEBHOOK (SECURE) - Uses gateway_salt for webhook secret
# ============================================================================

@csrf_exempt
@api_view(['GET', 'POST'])
def razporpay_webhook_url(request):
    """Razorpay Webhook Handler with Signature Verification"""
    if request.method == 'POST':
        
        # Get gateway details
        gateway_detail = PaymentGateway.objects.get(name='Razorpay')
        
        # STEP 1: Verify webhook signature FIRST (using gateway_salt)
        is_valid, error_message = verify_webhook_request(
            request, 
            'Razorpay', 
            gateway_detail.gateway_salt  # ← Webhook secret from database
        )
        
        if not is_valid:
            print(f"❌ Razorpay webhook verification failed: {error_message}")
            return JsonResponse(
                {'status': 'error', 'message': 'Invalid signature'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        print("✅ Razorpay webhook signature verified")
        
        # STEP 2: Process the webhook payload
        request_data = request.data
        
        # ... rest of your existing Razorpay webhook code ...
        # (Keep all the existing payment processing logic)
        
    return JsonResponse({'status': 'success'}, status=status.HTTP_200_OK)


# ============================================================================
# SPLIT RAZORPAY WEBHOOK (SECURE) - Uses gateway_salt for webhook secret
# ============================================================================

@csrf_exempt
@api_view(['GET', 'POST'])
def split_razporpay_webhook_url(request):
    """Split Razorpay Webhook Handler with Signature Verification"""
    if request.method == 'POST':
        
        # Get gateway details
        gateway_detail = PaymentGateway.objects.get(name='split_razorpay')
        
        # STEP 1: Verify webhook signature FIRST (using gateway_salt)
        is_valid, error_message = verify_webhook_request(
            request, 
            'split_razorpay', 
            gateway_detail.gateway_salt  # ← Webhook secret from database
        )
        
        if not is_valid:
            print(f"❌ Split Razorpay webhook verification failed: {error_message}")
            return JsonResponse(
                {'status': 'error', 'message': 'Invalid signature'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        print("✅ Split Razorpay webhook signature verified")
        
        # STEP 2: Process the webhook payload
        request_data = request.data
        
        # ... rest of your existing Split Razorpay webhook code ...
        # (Keep all the existing payment processing logic)
        
    return JsonResponse({'status': 'success'}, status=status.HTTP_200_OK)


# ============================================================================
# IMPLEMENTATION NOTES
# ============================================================================

"""
HOW TO UPDATE api_views.py:

1. Add import at top:
   from .webhook_security import verify_webhook_request

2. For razporpay_webhook_url function:
   - Add gateway_detail = PaymentGateway.objects.get(name='Razorpay')
   - Add verification code (see above)
   - Keep rest of existing code

3. For split_razporpay_webhook_url function:
   - Add gateway_detail = PaymentGateway.objects.get(name='split_razorpay')
   - Add verification code (see above)
   - Keep rest of existing code

WHAT HAPPENS:
- Webhook secret stored in gateway_salt field (database)
- No .env file needed
- If wrong secret → Payment FAILS (strict security)
- If no secret → Payment FAILS (strict security)
- If correct secret → Payment SUCCESS

ADMIN PANEL SETUP:
1. Go to: https://calculatentrade.com/admin/
2. AdminPortal → Payment gateways
3. Edit "Razorpay":
   - Gateway salt: Paste webhook secret from Razorpay dashboard
4. Edit "split_razorpay":
   - Gateway salt: Paste webhook secret from Razorpay dashboard
5. Save

TESTING:
- Correct secret → ✅ Payment works
- Wrong secret → ❌ Payment fails (401 error)
- No secret → ❌ Payment fails (401 error)
"""
