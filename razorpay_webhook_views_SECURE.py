"""
SECURE Razorpay Webhook Views with Signature Verification
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


@csrf_exempt
@api_view(['GET', 'POST'])
def razporpay_webhook_url(request):
    """
    Razorpay Webhook Handler with Signature Verification
    
    Security: Verifies webhook signature before processing payment
    """
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
        
        # get payment gateway from database
        gateway_detail = PaymentGateway.objects.get(name='Razorpay')
        client = razorpay.Client(auth=(gateway_detail.gateway_key, gateway_detail.gateway_secret))
        
        try:
            payment_id = request_data['payload']['payment']['entity']['id']
            order_id = request_data['payload']['payment']['entity']['order_id']
            razorpay_payment = RazorpayPayment.objects.get(razorpay_order_id=order_id)

            payment_status = request_data['payload']['payment']['entity']['status']
            
            if payment_status == 'captured':
                # get the payment data and save other informations also
                payment_data = client.payment.fetch(payment_id)
                # If verification is successful, update the payment status to success
                
                # if payment gateway is razorpay
                razorpay_payment = RazorpayPayment.objects.get(razorpay_order_id=order_id)
                payment = razorpay_payment.payment
                
                razorpay_payment.razorpay_payment_id = payment_id
                razorpay_payment.save()
                
                if payment.status != 'Success':
                    payment.payment_method = 'Gateway'
                    payment.phone_number = payment_data['contact']
                    payment.status = "Success"
                    payment.time=localtime(timezone.now())
                    payment.save()

                    seat = payment.order.seat
                    seat.is_vacent = False
                    seat.save()

                    order_status_url = reverse("theatre:order-status", args=[payment.order.pk])
                    order_status_url = f"https://www.scan2food.com{order_status_url}"
                    cusotmer_message = f"🎉 *Order Confirmed!* 🍿🥤%0A%0AThank you for your order, and welcome to *{seat.row.hall.theatre.name}*! 🎬✨%0A%0A🪑 *Your Seat:* {seat.row.hall.name}, {seat.name} %0A📍 *Track your order:* {order_status_url}%0A%0ASit back, relax, and enjoy your movie without missing a single scene!%0A%0A🚀 We'll deliver your food and drinks to your seat shortly.%0A%0Aℹ️ For assistance, contact our theatre staff at {seat.row.hall.theatre.query_number} 📞.%0A%0A⚠️ Please do not reply to this message or call this number.%0A%0AEnjoy the show! 🍿🎟️%0A%0A— *Team Scan2Food* 🚀"

                    order_profile_url = reverse("theatre:order-profile", args=[payment.order.pk])
                    order_profile_url = f"https://www.scan2food.com{order_profile_url}"

                    group = seat.row.hall.theatre.group
                    # update data on websocket
                    update_websocket(
                        theatre_id=seat.row.hall.theatre.id,
                        seat_id=seat.id,
                        is_vacent=seat.is_vacent,
                        payment_panding=False,
                        seat_name=f"{seat.row.hall.name} | {seat.name}",
                        message=f'New Order Come From Seat {seat.row.hall.name} | {seat.name}  %0A%0A Order Profile:- {order_profile_url}',
                        customer_phone=payment.order.payment.phone_number,
                        customer_message=cusotmer_message,
                        notification_numbers=seat.row.hall.theatre.notification_numbers,
                        group=group,
                        theatre_name=seat.row.hall.theatre.name,
                        msg_typ="confirmation",
                        payment_method=payment.payment_method,
                        payment_status=payment.status,
                        amount=payment.order.order_amount(),
                        order_id=payment.order.pk,
                        max_time=payment.order.max_time()
                    )
                    
                    print(f"✅ Payment processed successfully: Order {order_id}")

        except razorpay.errors.SignatureVerificationError:
            # If verification fails, mark the payment as failed
            print(f"❌ Razorpay signature verification error for order {order_id}")
            payment = Payment.objects.get(razorpay_order_id=order_id)
            payment.status = 'Failed'
            payment.save()
            return HttpResponse("Payment Failed")
        
        except Exception as e:
            print(f"❌ Error processing Razorpay webhook: {e}")
            return JsonResponse(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    return JsonResponse({'status': 'success'}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET', 'POST'])
def split_razporpay_webhook_url(request):
    """
    Split Razorpay Webhook Handler with Signature Verification
    
    Security: Verifies webhook signature before processing payment
    """
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
        
        # get payment gateway from database
        gateway_detail = PaymentGateway.objects.get(name='split_razorpay')
        client = razorpay.Client(auth=(gateway_detail.gateway_key, gateway_detail.gateway_secret))
        
        try:
            payment_id = request_data['payload']['payment']['entity']['id']
            order_id = request_data['payload']['payment']['entity']['order_id']
            razorpay_payment = SplitRazorpayPayment.objects.get(razorpay_order_id=order_id)

            payment_status = request_data['payload']['payment']['entity']['status']
            
            if payment_status == 'captured':
                # get the payment data and save other informations also
                payment_data = client.payment.fetch(payment_id)
                # If verification is successful, update the payment status to success
                
                # if payment gateway is razorpay
                razorpay_payment = SplitRazorpayPayment.objects.get(razorpay_order_id=order_id)
                payment = razorpay_payment.payment
                
                razorpay_payment.razorpay_payment_id = payment_id
                razorpay_payment.save()
                
                if payment.status != 'Success':
                    payment.payment_method = 'Gateway'
                    payment.phone_number = payment_data['contact']
                    payment.status = "Success"
                    payment.time=localtime(timezone.now())
                    payment.save()

                    seat = payment.order.seat
                    seat.is_vacent = False
                    seat.save()

                    order_status_url = reverse("theatre:order-status", args=[payment.order.pk])
                    order_status_url = f"https://www.scan2food.com{order_status_url}"
                    cusotmer_message = f"🎉 *Order Confirmed!* 🍿🥤%0A%0AThank you for your order, and welcome to *{seat.row.hall.theatre.name}*! 🎬✨%0A%0A🪑 *Your Seat:* {seat.row.hall.name}, {seat.name} %0A📍 *Track your order:* {order_status_url}%0A%0ASit back, relax, and enjoy your movie without missing a single scene!%0A%0A🚀 We'll deliver your food and drinks to your seat shortly.%0A%0Aℹ️ For assistance, contact our theatre staff at {seat.row.hall.theatre.query_number} 📞.%0A%0A⚠️ Please do not reply to this message or call this number.%0A%0AEnjoy the show! 🍿🎟️%0A%0A— *Team Scan2Food* 🚀"

                    order_profile_url = reverse("theatre:order-profile", args=[payment.order.pk])
                    order_profile_url = f"https://www.scan2food.com{order_profile_url}"

                    group = seat.row.hall.theatre.group
                    # update data on websocket
                    update_websocket(
                        theatre_id=seat.row.hall.theatre.id,
                        seat_id=seat.id,
                        is_vacent=seat.is_vacent,
                        payment_panding=False,
                        seat_name=f"{seat.row.hall.name} | {seat.name}",
                        message=f'New Order Come From Seat {seat.row.hall.name} | {seat.name}  %0A%0A Order Profile:- {order_profile_url}',
                        customer_phone=payment.order.payment.phone_number,
                        customer_message=cusotmer_message,
                        notification_numbers=seat.row.hall.theatre.notification_numbers,
                        group=group,
                        theatre_name=seat.row.hall.theatre.name,
                        msg_typ="confirmation",
                        payment_method=payment.payment_method,
                        payment_status=payment.status,
                        amount=payment.order.order_amount(),
                        order_id=payment.order.pk,
                        max_time=payment.order.max_time()
                    )
                    
                    print(f"✅ Split payment processed successfully: Order {order_id}")

        except razorpay.errors.SignatureVerificationError:
            # If verification fails, mark the payment as failed
            print(f"❌ Split Razorpay signature verification error for order {order_id}")
            payment = Payment.objects.get(razorpay_order_id=order_id)
            payment.status = 'Failed'
            payment.save()
            return HttpResponse("Payment Failed")
        
        except Exception as e:
            print(f"❌ Error processing Split Razorpay webhook: {e}")
            return JsonResponse(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    return JsonResponse({'status': 'success'}, status=status.HTTP_200_OK)
