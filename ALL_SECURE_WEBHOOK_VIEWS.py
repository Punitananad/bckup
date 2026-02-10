"""
SECURE Webhook Views for ALL Payment Gateways
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
import hashlib
import requests

from adminPortal.models import PaymentGateway
from .update_websocket import update_websocket
from .webhook_security import (
    verify_webhook_request,
    verify_payu_webhook,
    verify_phonepe_webhook,
    validate_ccavenue_webhook
)


# ============================================================================
# RAZORPAY WEBHOOK (SECURE)
# ============================================================================

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
        
        # STEP 2: Process the webhook payload
        request_data = request.data
        
        # ... rest of your existing Razorpay webhook code ...
        # (Keep all the existing payment processing logic)
        
    return JsonResponse({'status': 'success'}, status=status.HTTP_200_OK)


# ============================================================================
# SPLIT RAZORPAY WEBHOOK (SECURE)
# ============================================================================

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
        
        # STEP 2: Process the webhook payload
        request_data = request.data
        
        # ... rest of your existing Split Razorpay webhook code ...
        # (Keep all the existing payment processing logic)
        
    return JsonResponse({'status': 'success'}, status=status.HTTP_200_OK)


# ============================================================================
# PAYU WEBHOOK (SECURE)
# ============================================================================

@csrf_exempt
@api_view(['GET', 'POST'])
def payu_webhook_url(request):
    """PayU Webhook Handler with Hash Verification"""
    if request.method == 'POST':
        
        # Get gateway details
        gateway_detail = PaymentGateway.objects.get(name="PayU")
        
        # STEP 1: Verify webhook hash FIRST
        is_valid, error_message = verify_payu_webhook(request, gateway_detail.gateway_salt)
        
        if not is_valid:
            print(f"❌ PayU webhook hash verification failed: {error_message}")
            return JsonResponse(
                {'status': 'error', 'message': 'Invalid hash'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        print("✅ PayU webhook hash verified")
        
        # STEP 2: Process the webhook payload
        txn_id = request.POST.get('txnid')
        payu_payment = PayuPayment.objects.filter(uu_id=txn_id).first()
        
        if not payu_payment:
            print(f"❌ PayU payment not found: {txn_id}")
            return JsonResponse(
                {'status': 'error', 'message': 'Payment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        payment = payu_payment.payment
        order = payment.order
        status_value = request.POST.get('status')

        if status_value == 'success':
            order_id = request.POST.get('mihpayid')

            # Verify payment with PayU API (additional security)
            payment.payupayment.order_id = order_id
            hash_string = f"{gateway_detail.gateway_key}|verify_payment|{txn_id}|{gateway_detail.gateway_salt}"
            hashh = hashlib.sha512(hash_string.encode('utf-8')).hexdigest()

            url = "https://info.payu.in/merchant/postservice.php?form=2"
            payload = {
                "key": gateway_detail.gateway_key,
                "command": "verify_payment",
                "var1": txn_id,
                "hash": hashh
            }
            
            response = requests.post(url, data=payload)
            response_data = response.json()
            
            if response_data['transaction_details'][txn_id]['status'] == 'success':
                payment.payment_method = 'Gateway'
                payment.status = 'Success'
                payment.time = localtime(timezone.now())
                payment.save()
                payment.payupayment.save()

                # Update seat and send websocket
                seat = order.seat
                seat.is_vacent = False
                seat.save()
                
                # ... rest of your existing PayU webhook code ...
                # (Keep all the websocket update logic)
                
                print(f"✅ PayU payment processed successfully: {txn_id}")
        
    return JsonResponse({'status': 'success'}, status=status.HTTP_200_OK)


# ============================================================================
# PHONEPE WEBHOOK (SECURE)
# ============================================================================

@csrf_exempt
@api_view(['GET', 'POST'])
def phonepe_data_request(request):
    """PhonePe Webhook Handler with Signature Verification"""
    
    # Get gateway details
    gateway_detail = PaymentGateway.objects.get(name="Phonepe")
    
    # STEP 1: Verify webhook signature FIRST
    is_valid, error_message = verify_phonepe_webhook(request, gateway_detail.gateway_secret)
    
    if not is_valid:
        print(f"❌ PhonePe webhook signature verification failed: {error_message}")
        return JsonResponse(
            {'status': 'error', 'message': 'Invalid signature'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    print("✅ PhonePe webhook signature verified")
    
    # STEP 2: Process the webhook payload
    phonepe_data = request.data
    request_type = phonepe_data['type']
    
    if request_type == "CHECKOUT_ORDER_COMPLETED":
        # ... rest of your existing PhonePe webhook code ...
        # (Keep all the existing payment processing logic)
        
        print(f"✅ PhonePe payment processed successfully")
    
    return JsonResponse({'status': 'success'}, status=status.HTTP_200_OK)


# ============================================================================
# CCAVENUE WEBHOOK (SECURE)
# ============================================================================

@csrf_exempt
@api_view(['GET', 'POST'])
def ccavenue_hook(request):
    """CCAvenue Webhook Handler with Enhanced Validation"""
    try:
        gateway = PaymentGateway.objects.get(name='CCAvenue')
        working_key = gateway.working_key
        plain_text = request.POST.get('encResp')
        
        # STEP 1: Decrypt response (existing security)
        decResp = decrypt(plain_text, working_key)
        payment_data = {}
        decResp = decResp.split('&')
        for data in decResp:
            key, value = data.split('=')
            payment_data[key] = value

        # STEP 2: Validate payment data
        order_id = payment_data.get('order_id')
        ccavenue_payment = CCAvenuePayment.objects.filter(uu_id=order_id).first()
        
        if not ccavenue_payment:
            print(f"❌ CCAvenue payment not found: {order_id}")
            return JsonResponse(
                {'status': 'error', 'message': 'Payment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        order = ccavenue_payment.payment.order
        
        # STEP 3: Additional validation
        is_valid, error_message = validate_ccavenue_webhook(payment_data, order)
        
        if not is_valid:
            print(f"❌ CCAvenue webhook validation failed: {error_message}")
            return JsonResponse(
                {'status': 'error', 'message': error_message},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        print("✅ CCAvenue webhook validated")

        # STEP 4: Process payment
        if payment_data['order_status'] == 'Success':
            payment = ccavenue_payment.payment
            payment.payment_method = 'Gateway'
            payment.status = 'Success'
            payment.time = localtime(timezone.now())
            payment.ccavenuepayment.tracking_id = payment_data['tracking_id']
            payment.ccavenuepayment.bank_ref_no = payment_data['bank_ref_no']
            payment.ccavenuepayment.save()
            payment.save()

            # Update seat and send websocket
            seat = order.seat
            seat.is_vacent = False
            seat.save()
            
            # ... rest of your existing CCAvenue webhook code ...
            # (Keep all the websocket update logic)
            
            print(f"✅ CCAvenue payment processed successfully: {order_id}")

    except Exception as e:
        print(f"❌ Error processing CCAvenue webhook: {e}")
        return JsonResponse(
            {'status': 'error', 'message': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return JsonResponse({'status': 'success'}, status=status.HTTP_200_OK)


# ============================================================================
# NOTES FOR IMPLEMENTATION
# ============================================================================

"""
IMPORTANT: When replacing webhook views in api_views.py:

1. Add this import at the top:
   from .webhook_security import (
       verify_webhook_request,
       verify_payu_webhook,
       verify_phonepe_webhook,
       validate_ccavenue_webhook
   )

2. For each webhook function above:
   - Copy the signature verification code (STEP 1)
   - Keep your existing payment processing logic (STEP 2)
   - Add logging for debugging

3. The verification happens BEFORE payment processing
   - If verification fails → Return 401 error
   - If verification succeeds → Process payment as usual

4. Backward compatible:
   - If no webhook secret/salt configured → Log warning but allow
   - This prevents breaking existing functionality

5. Test thoroughly:
   - Test with real payments
   - Test with fake webhooks (should be rejected)
   - Monitor logs for verification messages
"""
