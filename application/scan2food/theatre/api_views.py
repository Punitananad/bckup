# DJANGO REST FRAME WORK
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.contrib import messages
from datetime import datetime, timedelta, time
# from .decorator import login_required
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, Q, Count, Max
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse, FileResponse
import json
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

# whatsapp template
from chat_box.whatsapp_msg_utils import amount_missmatch

# send data to websocket
from .update_websocket import update_websocket, send_invoice
from .webhook_security import verify_webhook_request

from django.urls import reverse
from django.contrib.auth.models import Permission
from django.utils.timezone import localtime
import razorpay
from django.conf import settings
import calendar
from adminPortal.models import PaymentGateway
from random import randint

# for razorpay imports
from requests.auth import HTTPBasicAuth

# cashfree imports for cashfree payments
from cashfree_pg.models.create_order_request import CreateOrderRequest
from cashfree_pg.api_client import Cashfree
from cashfree_pg.models.customer_details import CustomerDetails
from cashfree_pg.models.order_meta import OrderMeta
from cashfree_pg.models.order_create_refund_request import OrderCreateRefundRequest
# cashfree imports ends here...


# phonepe imports for phonepe payments
from uuid import uuid4
from phonepe.sdk.pg.payments.v2.standard_checkout_client import StandardCheckoutClient
from phonepe.sdk.pg.payments.v2.models.request.standard_checkout_pay_request import StandardCheckoutPayRequest
from phonepe.sdk.pg.env import Env
# phonepe imports ends here...

# payu imports for payu payments
import hashlib
import requests

# ccavenue imports for cavenue payments
from .views import decrypt

from django.views.decorators.csrf import csrf_exempt

import os

from adminPortal.models import PayOutLogs

# import all the theatre models to send data regarding the theatre
from .models import *
# sse implementations
from asgiref.sync import sync_to_async
from .sse_utils import get_all_orders

# CASHING FOR THE APPLICATION
from django.core.cache import cache

# Function to create the Hash for the PauU Gateway Application.
def generate_hash(params, salt):
    # Extract parameters or use empty string if not provided
    key = params['key']
    txnid = params['txnid']
    amount = params['amount']
    productinfo = params['productinfo']
    firstname = params['firstname']
    email = params['email']
    udf1 = params.get('udf1', '')
    udf2 = params.get('udf2', '')
    udf3 = params.get('udf3', '')
    udf4 = params.get('udf4', '')
    udf5 = params.get('udf5', '')
    
    # Construct hash string with exact parameter sequence
    hash_string = f"{key}|{txnid}|{amount}|{productinfo}|{firstname}|{email}|{udf1}|{udf2}|{udf3}|{udf4}|{udf5}||||||{salt}"
    
    # Generate SHA-512 hash
    return hashlib.sha512(hash_string.encode('utf-8')).hexdigest()
 

@never_cache
@login_required
@api_view(['GET'])
def all_seating_plan(request):
    return_data = {}
    theatre_hall = request.user.userprofile.theatre.hall_set.all()
    try:
        for hall in theatre_hall:
            return_data[hall.name] = {}
            for row in hall.row_set.all().order_by('id'):
                seat_list = []
                for seat in row.seat_set.all().order_by('id'):
                    seat_list_data = {"seat_id": seat.pk, "seat_name": seat.name, "is_vacent": seat.is_vacent}
                    if seat.is_vacent == False:
                        try:
                            last_order = seat.order_set.last()
                            payment_method = last_order.payment.payment_method
                            seat_list_data['payment_method'] = payment_method
                            seat_list_data['payment_status'] = last_order.payment.status
                            seat_list_data['is_shown'] = last_order.is_shown
                        except Exception:
                            if seat.order_set.last() == None:
                                seat.is_vacent = True
                                seat.save()
                            elif last_order.payment == None:
                                last_order.delete()
                            
                            else:
                                raise Exception

                    seat_list.append(seat_list_data)

                return_data[hall.name][row.name] = seat_list
    except Exception as e:
        return_data['message'] = 'Something went wrong'
        return_data['error'] = str(e)

    return JsonResponse(return_data)


@api_view(['POST'])
def theatre_detail(request):
    if request.method == 'POST':
        data = request.data
        theatre_id = data['theatre_id']

        cache_key = f"theatre-seating-{theatre_id}"
        cache_data = cache.get(cache_key)

        if cache_data:
            return JsonResponse(cache_data)
        
        else:
            theatre = Theatre.objects.get(pk=theatre_id)

            return_data = {}
            theatre_hall = theatre.hall_set.all()
            try:
                return_data['theatre_name'] = theatre.name
                seating = {}
                for hall in theatre_hall:
                    seating[hall.name] = {}
                    for row in hall.row_set.all().order_by('id'):
                        seat_list = []
                        for seat in row.seat_set.all().order_by('id'):
                            seat_list_data = {"seat_id": seat.pk, "seat_name": seat.name}
                            seat_list.append(seat_list_data)

                        seating[hall.name][row.name] = seat_list
                
                return_data['seating'] = seating
                return_data['is_error'] = False

                # UPDATE THE CACHE
                cache.set(cache_key, return_data, timeout=60 * 60 * 24)

            except Exception as e:
                return_data['is_error'] = True
                return_data['message'] = 'Something went wrong'
                return_data['error'] = str(e)
                

            return JsonResponse(return_data)
    else:
        return JsonResponse({'error': 'method not allowed'}, status=405)

# any body can access
@never_cache
@api_view(['GET'])
def all_menu(request, pk=None): 
    cache_key = f'theatre_menu_{pk}'
    cache_data = cache.get(cache_key)

    if cache_data:
        response = JsonResponse(cache_data, safe=False)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    
    data = {}
    return_data = []
    try:
        theatre = Theatre.objects.get(pk=pk)
        commission = theatre.commission_set.last()

        if commission == None:
            commission = 5.0
        
        else:
            commission = commission.commission_perscantage
    
        data['commission'] = commission
        detail = theatre.detail

        try:
            gst_detail = theatre.gstdetails
            if gst_detail.gst_state == 'Karnataka':
                data['tax_type'] = 'CGST'
            else:
                data['tax_type'] = 'IGST'
        except:
            data['tax_type'] = 'IGST'

        if detail.payment_model == 'theatre':
            commission = 0
        

        all_category = FoodCategory.objects.filter(theatre = theatre).annotate(max_priority=Max('fooditem__priority_number')).order_by('-max_priority')
        
        for category in all_category:
            category_image = f'{settings.STATIC_URL}assets/images/category/{category.name}.png'
            theatre_data = {"name": category.name, "id": category.pk, "category_image": category_image}
            food_items = []
            for item in category.fooditem_set.filter(is_approved=True).order_by('-priority_number'):
                # Handle food image with proper error checking
                try:
                    if item.food_image and hasattr(item.food_image, 'url'):
                        food_image = item.food_image.url
                    else:
                        # Use default image if no image is set
                        food_image = f'{settings.MEDIA_URL}default_food_img.png'
                except Exception as e:
                    # Fallback to default image on any error
                    food_image = f'{settings.MEDIA_URL}default_food_img.png'
                
                push_data = {
                    "item_id": item.id,
                    "name": item.name,
                    "description": item.description,
                    "real_price":item.discounted_price(),
                    "price": item.price,
                    "food_type": item.food_type,
                    "food_image": food_image,
                    "made_by": item.made_by,
                    "min_time": item.min_time,
                    "max_time": item.max_time
                    }

                discounted_price = item.discounted_price()

                updated_price = discounted_price + (discounted_price * commission / 100)
                push_data['price'] = round(updated_price, 2)

                if item.is_available:
                    food_items.append(push_data)

            theatre_data['items'] = food_items
            if food_items != []:
                return_data.append(theatre_data)

        data['all_category'] = return_data

        cache.set(cache_key, data, timeout=60 * 60 * 24)  # Cache for 1 day (86400 seconds)
    
    except:
        pass
    
    response = JsonResponse(data, safe=False)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

@api_view(['GET'])
def get_tex_list(request, pk):
    return_data = []
    try:
        theatre = Theatre.objects.get(pk=pk)
        all_taxes = theatre.tax_set.all()
        for tax in all_taxes:
            append_data = {"name": tax.name, "percentage": tax.percentage}
            return_data.append(append_data)
    except:
        pass

    return JsonResponse(return_data, safe=False)

@api_view(['GET'])
def order_data(request, pk):
    return_data = {}
    order = Order.objects.get(pk=pk)

    delivery_date = ""
    delivery_time = ""

    if order.delivery_time == None:
        food_delivered = False
    else:
        food_delivered = True
        delivery_complete_date = localtime(order.delivery_time)
        delivery_date = delivery_complete_date.strftime("%d-%b-%Y")
        delivery_time = delivery_complete_date.strftime("%I:%M %p")

    payment_pending = True
    amount_paid = 0
    payment_method = 'Pending'
    phone_number = ""
    payment_status = "Pending"
    try:
        payment = order.payment  # Directly access the payment using related_name
        phone_number = payment.phone_number
        payment_status = payment.status
        if payment.status == 'Success':
            payment_pending = False
            amount_paid = payment.order.order_amount()
            payment_method = payment.payment_method
        else:
            payment_pending = True
        
        if payment.status == 'Created':
            payment_status = 'Pending'

    except Payment.DoesNotExist:
        payment_pending == True
    

    # Get the localized time
    localized_time = localtime(order.start_time)

    return_data['order_detail'] = {
        "order_id": pk,
        "food_delivered": food_delivered,
        "order_date": order.start_time.strftime("%d-%b-%Y"),
        "order_time": localized_time.strftime("%I:%M %p"),
        "payment_pending": payment_pending,
        "payment_status": payment_status,
        "amount": amount_paid,
        "delivery_date": delivery_date,
        "delivery_time": delivery_time,
        "payment_method": payment_method,
        "phone_number": phone_number,
        "is_shown": order.is_shown,
        "notes": order.notes,
        "ratting": order.rating,
        "comment": order.comment,
        "payment_gateway": order.payment.gateway if hasattr(order, 'payment') else "",
        "gateway_order_id": order.get_gateway_order_id(),
        "payment_id": order.payment.pk if hasattr(order, 'payment') else "",
        }


    return_data['seat'] = f"{order.seat.row.hall.name} ({order.seat.name})"
    return_data['theatre_name'] = order.seat.row.hall.theatre.name
    return_data['seat_id'] = order.seat.pk
    return_data['order_amount'] = order.order_amount()
    return_data['order_items'] = []
    for item in order.items.all():
        try:
            food_item = item.food_item
            food_image = request.build_absolute_uri(food_item.food_image.url)
            max_time = item.food_item.max_time
            food_id = food_item.pk
            description = item.food_item.description
        except Exception as e:
            food_image = request.build_absolute_uri('/media/default_food_img.png')
            max_time = 30
            food_id = ""
            description = "item was deleted"

        push_data = {'name': item.name, "quantity": item.quantity, "price": item.price*item.quantity, "item-price": item.price, "food_image": food_image, "max_time": max_time, "id": food_id, "description": description}
        return_data['order_items'].append(push_data)
    
    return JsonResponse(return_data, safe=False)
    

@api_view(['GET'])
def seat_last_order(request, pk):
    return_data = {}
    seat = Seat.objects.get(pk=pk)
    order = seat.order_set.filter(payment__status='Success').last()
    delivery_date = ""
    delivery_time = ""
    payment_method = "Pending"
    phone_number = ""

    if order.delivery_time == None:
        food_delivered = False
    else:
        food_delivered = True
        delivery_complete_date = localtime(order.delivery_time)
        delivery_date = delivery_complete_date.strftime("%d-%b-%Y")
        delivery_time = delivery_complete_date.strftime("%I:%M %p")

        seat.is_vacent = True
        seat.save()

        # Update the websocket
        update_websocket(
            theatre_id=seat.row.hall.theatre.id,
            seat_id=seat.id,
            is_vacent=seat.is_vacent,
            payment_panding=False,
            seat_name=f"{seat.row.hall.name} | {seat.name}",
            message=f'Order Successfully Deliver To Seat: {seat.row.hall.name}, {seat.name}',
            msg_typ='Delivered',
            order_id=order.pk,        
        )

    payment_pending = True
    amount_paid = 0

    try:
        payment = order.payment  # Directly access the payment using related_name
        phone_number = payment.phone_number
        payment_status = payment.status
        if payment.status == 'Success':
            payment_pending = False
            amount_paid = payment.order.order_amount()
            payment_method = payment.payment_method
        else:
            payment_pending = True
        
        if payment.status == 'Created':
            payment_status = 'Pending'

    except Payment.DoesNotExist:
        payment_pending == True
    

    # Get the localized time
    localized_time = localtime(order.start_time)
    
    return_data['order_detail'] = {
        "order_id": order.pk,
        "food_delivered": food_delivered,
        "order_date": order.start_time.strftime("%d-%b-%Y"),
        "order_time": localized_time.strftime("%I:%M %p"),
        "payment_pending": payment_pending,
        "payment_status": payment_status,
        "amount": amount_paid,
        "delivery_date": delivery_date,
        "delivery_time": delivery_time,
        "payment_method": payment_method,
        "phone_number": phone_number,
        "is_shown": order.is_shown,
        "notes": order.notes,
        "ratting": order.rating,
        "comment": order.comment,
        "payment_gateway": order.payment.gateway if hasattr(order, 'payment') else "",
        "gateway_order_id": order.get_gateway_order_id(),
        "payment_id": order.payment.pk if hasattr(order, 'payment') else "",
        }
    
    return_data['seat'] = f"{order.seat.row.hall.name} ({order.seat.name})"
    return_data['theatre_name'] = order.seat.row.hall.theatre.name
    return_data['seat_id'] = order.seat.pk
    return_data['order_amount'] = order.order_amount()
    return_data['order_items'] = []
    for item in order.items.all():
        try:
            food_item = item.food_item
            food_image = request.build_absolute_uri(food_item.food_image.url)
            max_time = item.food_item.max_time
            food_id = food_image.pk
            description = item.food_item.description

        except:
            food_image = request.build_absolute_uri('/media/default_food_img.png')
            max_time = 30
            food_id = ""
            description = "item was deleted"
            
        push_data = {'name': item.name, "quantity": item.quantity, "price": item.price*item.quantity, "item-price": item.price, "food_image": food_image, "max_time": max_time, "id": food_id, "description": description}
        return_data['order_items'].append(push_data)
    
    return JsonResponse(return_data, safe=False)


@csrf_exempt
@csrf_exempt
@csrf_exempt
@api_view(['POST'])
def create_order(request):
    current_user = request.user

    return_data = {}
    # Parse the JSON body
    data = request.data

    # Access the data
    theatre_id = data.get('theatre_id')
    
    seat = data.get('seat')
    
    cart_data = data.get('cart_data')

    hall_name = seat.split("|")[0][: -1]

    seat_name = seat.split("|")[1].replace(" ", "")

    seat = Seat.objects.filter(name=seat_name, row__hall__name=hall_name, row__hall__theatre__id=theatre_id).first()
    theatre = seat.row.hall.theatre

    is_user = True
    if str(current_user) == 'AnonymousUser':
        is_user = False

    if is_user == True:
        try:
            if (request.user.userprofile.theatre.pk == theatre_id):
                pass
            else:
                is_user = False
        except:
            is_user = False

    if seat.is_vacent == False:
        url = reverse('theatre:show-menu', kwargs={'pk', seat.pk})
        return_data['url'] = url
        return JsonResponse(return_data)
    
    # create new order
    if is_user:
        new_order = Order.objects.create(seat=seat, taken_by=current_user)
    else:
        new_order = Order.objects.create(seat=seat)
    
    
    new_amount = 0
    order_amount = 0
    for n in cart_data:
        # creating order items
        item_data = cart_data[n]
        item = FoodItem.objects.get(pk=n)
        OrderItems.objects.create(
            order=new_order,
            name=item.name,
            quantity=item_data['quantity'],
            price=item.discounted_price(),
            food_item=item,
            )
        
        new_amount += float(item_data['item_price']) * item_data['quantity']
        order_amount += float(item.price) * item_data['quantity']
    
    if new_amount == 0:
        messages.error(request, 'Please add some items to the cart')
        new_order.delete()
        return_data['url'] = reverse('theatre:show-menu', kwargs={'pk': seat.pk})
        return JsonResponse(return_data, status=status.HTTP_400_BAD_REQUEST)

    new_amount = new_amount * 100

    new_amount = round(new_amount, 2)

    order_amount = order_amount * 100
    order_amount = round(order_amount, 2)
    
    # get the settlement model
    settlement_model = theatre.detail.settlement_model
    if settlement_model == 'Split':
        selected_gateway = theatre.detail.selected_gateway
    
    else:
        selected_gateway = PaymentGateway.objects.filter(is_active=True).first()

    payment_model = new_order.seat.row.hall.theatre.detail.payment_model
    if payment_model == 'theatre':
        commission = seat.row.hall.theatre.commission_set.last()
        if commission == None:
            commission = 5.0
        else:
            commission = commission.commission_perscantage

        settlement = (new_amount / 100) * (commission / 100)
    else:
        settlement = 0
        

    # initate payment
    payment = Payment.objects.create(
        order=new_order,
        status = 'Created',
        amount = new_amount / 100,
        gateway = selected_gateway.name,
        settlement = settlement
    )

    # if razorpay payment method is selected

    if settlement_model == 'Split':
        if selected_gateway.name == 'split_razorpay':
            payment.invoice_comp = "SCAN2FOOD"
            payment.gateway = 'split_razorpay'
            payment.save()
            client = razorpay.Client(auth=(selected_gateway.gateway_key, selected_gateway.gateway_secret))
            account_id = theatre.detail.razorpay_id

            settlement_amount = settlement * 100
            theatre_amount = order_amount - settlement_amount

            if account_id != "":
                razorpay_order = client.order.create({
                    'amount': new_amount, # Total amount of the order
                    'currency': 'INR',
                    'payment_capture': '1',  # Automatically capture payment
                    'transfers': [
                        {
                            'account': account_id,
                            'amount': theatre_amount, # The ammount of the Theatre, which sent to the Theatre on spliting
                            "currency": "INR",
                            "notes": {
                                "purpose": "Theatre Payment"
                            }
                        }
                    ]
                })

                # create razorpay payment in database
                SplitRazorpayPayment.objects.create(
                    payment=payment,
                    razorpay_order_id=razorpay_order['id']
                )

                return_data['url'] = reverse('theatre:initiate-payment', kwargs={'pk': new_order.pk})
                return JsonResponse(return_data)
    
    
    if selected_gateway.name == 'split_razorpay':
        payment.invoice_comp = "SCAN2FOOD"
        payment.gateway = 'split_razorpay'
        payment.save()
        client = razorpay.Client(auth=(selected_gateway.gateway_key, selected_gateway.gateway_secret))

        # create razorpay order
        razorpay_order = client.order.create({
            'amount': new_amount,
            'currency': 'INR',
            'payment_capture': '1',  # Automatically capture payment
        })
        # create razorpay payment in database
        SplitRazorpayPayment.objects.create(
            payment=payment,
            razorpay_order_id=razorpay_order['id']
        )
    
    if selected_gateway.name == 'Razorpay':
        payment.invoice_comp = "SCAN2FOOD"
        payment.gateway = 'Razorpay'
        payment.save()
        client = razorpay.Client(auth=(selected_gateway.gateway_key, selected_gateway.gateway_secret))

        # create razorpay order
        razorpay_order = client.order.create({
            'amount': new_amount,
            'currency': 'INR',
            'payment_capture': '1',  # Automatically capture payment
        })
        # create razorpay payment in database
        RazorpayPayment.objects.create(
            payment=payment,
            razorpay_order_id=razorpay_order['id']
        )
    
    elif selected_gateway.name == 'Cashfree':
        payment.invoice_comp = 'DOP AGENT SOFTWARE'
        payment.gateway = 'Cashfree'
        payment.save()
        app_id = selected_gateway.gateway_key
        secret_key = selected_gateway.gateway_secret
        
        # create cashfree order
        Cashfree.XClientId = app_id
        Cashfree.XClientSecret = secret_key
        Cashfree.XEnvironment = Cashfree.PRODUCTION # SANDBOX or PRODUCTION
        x_api_version = "2023-08-01"

        # create order request
        theatre = payment.order.seat.row.hall.theatre
        customer_name = f"{theatre.name} {theatre.owner_name}"
        customer_email = f"{payment.order.pk}@scan2food.com"
        customerDetails = CustomerDetails(customer_id=f"scan2food_{theatre.pk}", customer_phone=theatre.phone_number, customer_name=customer_name, customer_email=customer_email)
        callback_url = request.build_absolute_uri('/theatre/api/cashfree-data-request')
        callback_url = callback_url.replace('http', 'https')
        orderMeta = OrderMeta(return_url=callback_url)
        createOrderRequest = CreateOrderRequest(
            order_amount=payment.amount,
            order_currency="INR",
            customer_details=customerDetails,
            order_meta=orderMeta
            )
        
        api_response = Cashfree().PGCreateOrder(x_api_version, createOrderRequest, None, None)
        data = api_response.data
        data = data.json()
        data = json.loads(data)

        # ORDER ID , PAYMENT_SESSION_ID HAVE TO SAVE IN DATABASE
        order_id = data['order_id']
        payment_session_id = data['payment_session_id']

        # create cashfree payment in database
        CashFreePayment.objects.create(
            payment=payment,
            cashfree_order_id=order_id,
            payment_session_id=payment_session_id
        )

    elif selected_gateway.name == 'Phonepe':
        payment.invoice_comp = "SCAN2FOOD"
        payment.gateway = 'Phonepe'
        payment.save()

        client_id = selected_gateway.gateway_key
        client_secret = selected_gateway.gateway_secret
        
        client_version = 1  
        # testing
        # Env.SANDBOX for testing and Env.PRODUCTION for real gateway
        env=Env.PRODUCTION

        client = StandardCheckoutClient.get_instance(client_id=client_id,
                                                            client_secret=client_secret,
                                                            client_version=client_version,
                                                            env=env)

        unique_order_id = str(uuid4())
        ui_redirect_url = request.build_absolute_uri(reverse('theatre:phonepe-payment-callback', args=[payment.order.pk]))
        amount = payment.amount * 100

        standard_pay_request = StandardCheckoutPayRequest.build_request(merchant_order_id=unique_order_id,
                                                                        amount=amount,
                                                                        redirect_url=ui_redirect_url)
        
        standard_pay_response = client.pay(standard_pay_request)
        # checkout_page_url = standard_pay_response.redirect_url
        order_id = standard_pay_response.order_id

        payment_url = standard_pay_response.redirect_url
        # save data in phonepe model in database
        PhonepePayment.objects.create(
            payment = payment,
            uu_id = unique_order_id,
            order_id = order_id,
            payment_url = payment_url
        )

    elif selected_gateway.name == 'PayU':
        # code for PayU
        payment.invoice_comp = 'SCAN2FOOD'
        payment.gateway = 'PayU'
        payment.save()

        unique_order_id = str(uuid4())

    elif selected_gateway.name == 'ccavenue':
        # HERE PAYMENT IS ALREADY CREATED WE HAVE TO CREATE THE CCAVANUE PAYMENT
        Payment.invoice_comp = 'SCAN2FOOD'
        payment.gateway = 'CCAvenue'
        payment.save()
        unique_order_id = str(uuid4())


    return_data['url'] = reverse('theatre:initiate-payment', kwargs={'pk': new_order.pk})
    return JsonResponse(return_data)

    
@login_required
@api_view(['GET'])
def deliver_order(request, pk):
    return_data = {}
    permission = Permission.objects.get(codename="view_order")
    if request.user.groups.first().permissions.filter(id=permission.id).exists():
        order = Order.objects.get(pk=pk)
        if request.user.userprofile.theatre == order.seat.row.hall.theatre:
            if order.delivery_time == None:
                try:
                    payment = order.payment
                    if payment.status == 'Success':
                        # update the order
                        order.delivered_by = request.user
                        order.delivery_time = localtime(timezone.now())
                        order.save()
                        
                        seat = order.seat
                        seat.is_vacent = True
                        seat.save()

                        # Update the websocket
                        update_websocket(
                            theatre_id=seat.row.hall.theatre.id,
                            seat_id=seat.id,
                            is_vacent=seat.is_vacent,
                            payment_panding=False,
                            seat_name=f"{seat.row.hall.name} | {seat.name}",
                            message=f'Order Successfully Deliver To Seat: {seat.row.hall.name}, {seat.name}',
                            msg_typ='Delivered',
                            order_id=order.pk,
                        )

                        return_data['message'] = f'Order Successfully Deliver To Seat: {seat.row.hall.name} | {seat.name}'

                        # send whatsapp message if require
                        if seat.row.hall.theatre.detail.payment_model != 'theatre':
                            phone_number = ""
                            customer_phone = order.payment.phone_number
                            if "+91" in customer_phone:
                                phone_number = customer_phone.replace("+", "")
                            else:
                                phone_number = f"91{customer_phone}"

                            send_invoice(phone_number=phone_number, order_pk=order.pk)

                    else:
                        return_data['message'] = 'Payment of this order is not completed Yet'
                except:
                    return_data['message'] = 'Payment Not Exist'
            else:
                return_data['message'] = 'Order is Already Delivered'
        
        else:
            return_data['message'] = 'Permission Denied'            

    else:
        return_data['message'] = 'Permission Denied'
    return JsonResponse(return_data)

@login_required
@api_view(['GET'])
def dashboard_data(request):
    theatre = request.user.userprofile.theatre
    date_range = request.GET.get('daterange', "")
    if date_range == "":
        current_time = localtime(timezone.now())
        current_time = current_time.replace(tzinfo=None)

        # get current hour
        if current_time.hour < 6:
            # if current time is more then 12 and less then 6:Am
            # its now previous date
            start_time = current_time - timedelta(days=1)
            # get start time with 6:00 Am
            start_time = start_time.replace(hour=6, minute=0, second=0, microsecond=0)

            end_time = current_time.replace(hour=6, minute=0, second=0, microsecond=0)

        else:
            # if current time is more then 6:00 Am
            end_time = current_time + timedelta(days=1)
            end_time = end_time.replace(hour=6, minute=0, second=0, microsecond=0)

            start_time = current_time.replace(hour=6, minute=0, second=0, microsecond=0)
            
    else:
        try:
            start_date = date_range.split(" - ")[0]
            end_date = date_range.split(" - ")[1]

            start_time_date = datetime.strptime(start_date, "%d/%b/%Y").date()
            end_time_date = datetime.strptime(end_date, "%d/%b/%Y").date()

            tiem_obj = time(hour=6, minute=0, second=0, microsecond=0)
            start_time = datetime.combine(start_time_date, tiem_obj)
            end_time = datetime.combine(end_time_date, tiem_obj)

        except :
            current_time = localtime(timezone.now())
            # get current hour
            if current_time.hour < 6:
                # if current time is more then 12 and less then 6:Am
                # its now previous date
                start_time = current_time - timedelta(days=1)
                # get start time with 6:00 Am
                start_time = start_time.replace(hour=6, minute=0, second=0, microsecond=0)

                end_time = current_time.replace(hour=6, minute=0, second=0, microsecond=0)

            else:
                # if current time is more then 6:00 Am
                end_time = current_time + timedelta(days=1)
                end_time = end_time.replace(hour=6, minute=0, second=0, microsecond=0)

                start_time = current_time.replace(hour=6, minute=0, second=0, microsecond=0)

    all_orders = Order.objects.filter(seat__row__hall__theatre=theatre, payment__status='Success', start_time__range=(start_time, end_time))
    
    staff_orders = all_orders.filter(taken_by__isnull=False).count()
    self_orders = all_orders.count() - staff_orders


    total_payment = Payment.objects.filter(order__in=all_orders, status='Success')

    total_payment = sum(payment.order.full_payment() for payment in total_payment)

    running_orders = Seat.objects.filter(row__hall__theatre=theatre, is_vacent = False).count()

    top_ordered_items = (
        OrderItems.objects
        .filter(order__in=all_orders)  # Filter OrderItems based on the retrieved orders
        .values('name')  # Group by item name
        .annotate(order_count=Sum('quantity'))  # Count occurrences
        .order_by('-order_count')[:5]  # Get top 5 most ordered items
    )

    top_selling_items = {}

    # Print results
    for item in top_ordered_items:
        top_selling_items[item['name']] = item['order_count']


    return_data = {
        "all_orders": all_orders.count(),
        "staff_orders": staff_orders,
        "self_orders": self_orders,
        "Total Payment": total_payment,
        "running_orders": running_orders,
        "top_selling_items": top_selling_items
        }
    
    return JsonResponse(return_data)

@api_view(['GET'])
def get_yearly_revenue(request, year):
    revenue_by_month = {}
    return JsonResponse(revenue_by_month)

@api_view(['GET'])
@login_required
def get_volet_data(request):
    return_data = {"unsettled_payment": 0}
    try:
    
        theatre = request.user.userprofile.theatre
        pending_payments = Payment.objects.filter(order__seat__row__hall__theatre=theatre, is_settled=False, status='Success', payment_method='Gateway')

        if pending_payments.count() == 0:
            current_balance = 0
        else:
            current_balance = sum(payment.order.full_payment() for payment in pending_payments)

        return_data['unsettled_payment'] = current_balance or 0
    
    except Exception as e:
        pass
    return JsonResponse(return_data)

@csrf_exempt
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
            
            # CRITICAL: Initiate refund for failed webhook verification
            # This prevents customer money loss when webhook is compromised
            try:
                request_data = request.data
                payment_id = request_data['payload']['payment']['entity']['id']
                order_id = request_data['payload']['payment']['entity']['order_id']
                
                # Get payment details
                razorpay_payment = RazorpayPayment.objects.get(razorpay_order_id=order_id)
                payment = razorpay_payment.payment
                
                # Mark payment as failed
                payment.status = 'Failed'
                payment.save()
                
                # Initiate refund via Razorpay API
                client = razorpay.Client(auth=(gateway_detail.gateway_key, gateway_detail.gateway_secret))
                refund = client.payment.refund(payment_id, {
                    "amount": int(payment.amount * 100),  # Amount in paise
                    "speed": "normal",
                    "notes": {
                        "reason": "Webhook verification failed - security issue"
                    }
                })
                print(f"✅ Refund initiated for payment {payment_id}: {refund['id']}")
                
            except Exception as e:
                print(f"❌ Failed to initiate refund: {str(e)}")
            
            return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=401)
        print("✅ Razorpay webhook verified")

        request_data = request.data
        
        client = razorpay.Client(auth=(gateway_detail.gateway_key, gateway_detail.gateway_secret))
        try:
            payment_id = request_data['payload']['payment']['entity']['id']
            order_id = request_data['payload']['payment']['entity']['order_id']
            razorpay_payment = RazorpayPayment.objects.get(razorpay_order_id=order_id)

            payment_status = request_data['payload']['payment']['entity']['status']
            if payment_status == 'captured':
                # get payment gateway from database
                gateway_detail = PaymentGateway.objects.get(name='Razorpay')
                client = razorpay.Client(auth=(gateway_detail.gateway_key, gateway_detail.gateway_secret))

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

        except razorpay.errors.SignatureVerificationError:
            # If verification fails, mark the payment as failed
            payment = Payment.objects.get(razorpay_order_id=order_id)
            payment.status = 'Failed'
            payment.save()
            # Perform any task on failure
            return HttpResponse("Payment Failed")


    return JsonResponse({'status': 'success'}, status=status.HTTP_200_OK)

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
            
            # CRITICAL: Initiate refund for failed webhook verification
            # This prevents customer money loss when webhook is compromised
            try:
                request_data = request.data
                payment_id = request_data['payload']['payment']['entity']['id']
                order_id = request_data['payload']['payment']['entity']['order_id']
                
                # Get payment details
                razorpay_payment = SplitRazorpayPayment.objects.get(razorpay_order_id=order_id)
                payment = razorpay_payment.payment
                
                # Mark payment as failed
                payment.status = 'Failed'
                payment.save()
                
                # Initiate refund via Razorpay API
                client = razorpay.Client(auth=(gateway_detail.gateway_key, gateway_detail.gateway_secret))
                refund = client.payment.refund(payment_id, {
                    "amount": int(payment.amount * 100),  # Amount in paise
                    "speed": "normal",
                    "notes": {
                        "reason": "Webhook verification failed - security issue"
                    }
                })
                print(f"✅ Refund initiated for payment {payment_id}: {refund['id']}")
                
            except Exception as e:
                print(f"❌ Failed to initiate refund: {str(e)}")
            
            return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=401)
        print("✅ Split Razorpay webhook verified")

        request_data = request.data
        
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

        except razorpay.errors.SignatureVerificationError:
            # If verification fails, mark the payment as failed
            payment = Payment.objects.get(razorpay_order_id=order_id)
            payment.status = 'Failed'
            payment.save()
            # Perform any task on failure
            return HttpResponse("Payment Failed")

    return JsonResponse({'status': 'success'}, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['GET', 'POST'])
def split_razporpay_payout_webhook(request):
    if request.method == 'POST':
        try:
            request_data = request.data
            
            account_id = request_data['account_id']
            settlement_amt = request_data['payload']['settlement']['entity']['amount']

            theatre = Theatre.objects.filter(detail__razorpay_id=account_id).first()
            # calculate the theatre payout
            current_time = localtime(timezone.now())

            last_time = current_time.replace(hour=6, minute=0, second=0, microsecond=0)
            
            pending_payments = Payment.objects.filter(is_settled=False, status='Success', payment_method='Gateway', time__lt=last_time, order__seat__row__hall__theatre=theatre)

            theatre_payments_amt = sum(payment.order.full_payment() for payment in pending_payments)
            theatre_payments_amt = int(theatre_payments_amt) * 100
            difference = abs(theatre_payments_amt - settlement_amt)
            
            if difference >= 10000:
                calculated_amt = settlement_amt / 100
                payout_amt = theatre_payments_amt / 100
                diff = difference / 100
                amount_missmatch(phone_number="917988994210", theatre_name=theatre.name, payout_amount=payout_amt,calculated_amount=calculated_amt, difference=diff)
                raise ValueError(f"Amount mismatch: expected {theatre_payments_amt}, but received {settlement_amt} theatre Name : {theatre.name} on {datetime.now().strftime("%I:%M:%p | %b %d, %Y")}")

            # create the payout
            last_payout = theatre.payoutlogs_set.last()

            if last_payout == None:
                first_payment = pending_payments.first()
                start_time = localtime(first_payment.time)
            
            else:
                first_payment = last_payout.end_time
                start_time = localtime(first_payment)
            
            theatre_payments_amt = theatre_payments_amt / 100
            payout = PayOutLogs.objects.create(start_time=start_time, end_time=last_time, amount=theatre_payments_amt, theatre=theatre)
            for payment in pending_payments:
                payment.payout = payout
                payment.is_settled = True
                payment.save()



        except Exception as e:
            pass
    return JsonResponse({'status': 'success'}, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['GET', 'POST'])
def cashfree_data_request(request):
    try:
        str_data = request.data
        str_data = str(str_data)
        data = str_data.replace('None','null')
        data = data.replace("'", '"')
        
        data = json.loads(data)
        order_id = data['data']['order']['order_id']

        cashfree_payment = CashFreePayment.objects.get(cashfree_order_id=order_id)
        payment = cashfree_payment.payment

        if payment.status != 'Success':

            gateway_detail = PaymentGateway.objects.get(name='Cashfree')

            Cashfree.XClientId = gateway_detail.gateway_key
            Cashfree.XClientSecret = gateway_detail.gateway_secret
            Cashfree.XEnvironment = Cashfree.PRODUCTION # SANDBOX or PRODUCTION
            x_api_version = "2023-08-01"
            order_id = payment.cashfreepayment.cashfree_order_id
            api_response = Cashfree().PGFetchOrder(x_api_version, order_id, None)
            data = api_response.data
            data = data.json()
            new_data = json.loads(data)
            order_status = new_data['order_status']
            if order_status == 'PAID':
                # UPDATE THE PAYMENT STATUS
                payment.payment_method = 'Gateway'
                payment.status = "Success"
                payment.time=localtime(timezone.now())
                payment.save()


                # UPDATE THE SEAT STATUS VIA WEBSOCKET ONLY WHEN PAYMENT IS SUCCESS AND SEAT IS NOT VACENT
                seat = payment.order.seat
                
                seat.is_vacent = False
                seat.save()
                order_status_url = reverse("theatre:order-status", args=[payment.order.pk])
                order_status_url = f"https://www.scan2food.com{order_status_url}"
                cusotmer_message = f"🎉 *Order Confirmed!* 🍿🥤%0A%0AThank you for your order, and welcome to *{seat.row.hall.theatre.name}*! 🎬✨%0A%0A🪑 *Your Seat:* {seat.row.hall.name}, {seat.name} %0A📍 *Track your order:* {order_status_url}%0A%0ASit back, relax, and enjoy your movie without missing a single scene!%0A%0A🚀 We'll deliver your food and drinks to your seat shortly.%0A%0Aℹ️ For assistance, contact our theatre staff at {seat.row.hall.theatre.query_number} 📞.%0A%0A⚠️ Please do not reply to this message or call this number.%0A%0AEnjoy the show! 🍿🎟️%0A%0A— *Team Scan2Food* 🚀"

                order_profile_url = reverse("theatre:order-profile", args=[payment.order.pk])
                order_profile_url = f"https://www.scan2food.com{order_profile_url}"

                group = seat.row.hall.theatre.group
                # update the data on websocket
                update_websocket(
                    theatre_id=seat.row.hall.theatre.id,
                    seat_id=seat.id,
                    is_vacent=seat.is_vacent,
                    payment_panding=False,
                    seat_name=f"{seat.row.hall.name} | {seat.name}",
                    message=f'New Order Come From Seat {seat.row.hall.name} | {seat.name} %0A%0A Order Profile:- {order_profile_url}',
                    customer_phone=payment.phone_number,
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

        return JsonResponse({'status': 'done'})
    except:
        return JsonResponse({'status': 'error'})
    
@csrf_exempt
@api_view(['GET', 'POST'])
def phonepe_data_request(request):
    phonepe_data = request.data
    
    request_type = phonepe_data['type']
    
    if request_type == "CHECKOUT_ORDER_COMPLETED":
        # payment is completed of an order 
        uuid = phonepe_data['payload']['merchantOrderId']
        try:
            phonepe_payment = PhonepePayment.objects.filter(uu_id = uuid).first()
            payment = phonepe_payment.payment
            order = payment.order
            if payment.status == 'Refunded':
                pass

            elif payment.status != 'Success':
                gateway_detail = PaymentGateway.objects.get(name="Phonepe")
                client_id = gateway_detail.gateway_key
                client_secret = gateway_detail.gateway_secret
                
                client_version = 1  
                # testing
                # Env.SANDBOX for testing and Env.PRODUCTION for real gateway
                env=Env.PRODUCTION

                client = StandardCheckoutClient.get_instance(client_id=client_id,
                                                                    client_secret=client_secret,
                                                                    client_version=client_version,
                                                                    env=env)
                
                unique_order_id = payment.phonepepayment.uu_id
                order_response = client.get_order_status(merchant_order_id=unique_order_id)
                order_status = order_response.state
            
                if order_status == "COMPLETED":
                    # UPDATE THE PAYMENT STATUS
                    payment.payment_method = 'Gateway'
                    payment.status = "Success"
                    payment.time=localtime(timezone.now())
                    payment.save()


                    # UPDATE THE SEAT STATUS VIA WEBSOCKET ONLY WHEN PAYMENT IS SUCCESS AND SEAT IS NOT VACENT
                    seat = payment.order.seat
                    
                    seat.is_vacent = False
                    seat.save()
                    order_status_url = reverse("theatre:order-status", args=[payment.order.pk])
                    order_status_url = f"https://www.scan2food.com{order_status_url}"
                    cusotmer_message = f"🎉 *Order Confirmed!* 🍿🥤%0A%0AThank you for your order, and welcome to *{seat.row.hall.theatre.name}*! 🎬✨%0A%0A🪑 *Your Seat:* {seat.row.hall.name}, {seat.name} %0A📍 *Track your order:* {order_status_url}%0A%0ASit back, relax, and enjoy your movie without missing a single scene!%0A%0A🚀 We'll deliver your food and drinks to your seat shortly.%0A%0Aℹ️ For assistance, contact our theatre staff at {seat.row.hall.theatre.query_number} 📞.%0A%0A⚠️ Please do not reply to this message or call this number.%0A%0AEnjoy the show! 🍿🎟️%0A%0A— *Team Scan2Food* 🚀"

                    order_profile_url = reverse("theatre:order-profile", args=[order.pk])
                    order_profile_url = f"https://www.scan2food.com{order_profile_url}"

                    group = seat.row.hall.theatre.group

                    # send data to websocket
                    update_websocket(
                        theatre_id=seat.row.hall.theatre.id,
                        seat_id=seat.id,
                        is_vacent=seat.is_vacent,
                        payment_panding=False,
                        seat_name=f"{seat.row.hall.name} | {seat.name}",
                        message=f'New Order Come From Seat {seat.row.hall.name} | {seat.name}  %0A%0A Order Profile:- {order_profile_url}',
                        customer_phone=order.payment.phone_number,
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

        except:
            pass

    return JsonResponse({'status': 'done'})

@csrf_exempt
@api_view(['GET', 'POST'])
def payu_webhook_url(request):
    if request.method == 'POST':            
        txn_id = request.POST.get('txnid')
        payu_payment = PayuPayment.objects.filter(uu_id=txn_id).first()
        payment = payu_payment.payment
        gateway_detail = PaymentGateway.objects.get(name="PayU")
        order = payment.order

        status = request.POST.get('status')

        if status == 'success':
            order_id = request.POST.get('mihpayid')

            # check from the payu gateway
            payment.payupayment.order_id = order_id
            hash_string = f"{gateway_detail.gateway_key}|verify_payment|{txn_id}|{gateway_detail.gateway_salt}"

            hashh = hashlib.sha512(hash_string.encode('utf-8')).hexdigest()

            url = "https://info.payu.in/merchant/postservice.php?form=2"
            # # url = "https://test.payu.in/merchant/postservice?form=2"

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
                payment.time=localtime(timezone.now())
                payment.save()
                payment.payupayment.save()


                seat = order.seat
                seat.is_vacent = False
                seat.save()
                order_status_url = reverse("theatre:order-status", args=[payment.order.pk])
                order_status_url = f"https://www.scan2food.com{order_status_url}"
                cusotmer_message = f"🎉 *Order Confirmed!* 🍿🥤%0A%0AThank you for your order, and welcome to *{seat.row.hall.theatre.name}*! 🎬✨%0A%0A🪑 *Your Seat:* {seat.row.hall.name}, {seat.name} %0A📍 *Track your order:* {order_status_url}%0A%0ASit back, relax, and enjoy your movie without missing a single scene!%0A%0A🚀 We'll deliver your food and drinks to your seat shortly.%0A%0Aℹ️ For assistance, contact our theatre staff at {seat.row.hall.theatre.query_number} 📞.%0A%0A⚠️ Please do not reply to this message or call this number.%0A%0AEnjoy the show! 🍿🎟️%0A%0A— *Team Scan2Food* 🚀"

                order_profile_url = reverse("theatre:order-profile", args=[order.pk])
                order_profile_url = f"https://www.scan2food.com{order_profile_url}"

                group=seat.row.hall.theatre.group

                # update websocket
                update_websocket(
                    theatre_id=seat.row.hall.theatre.id,
                    seat_id=seat.id,
                    is_vacent=seat.is_vacent,
                    payment_panding=False,
                    seat_name=f"{seat.row.hall.name} | {seat.name}",
                    message=f'New Order Come From Seat {seat.row.hall.name} | {seat.name}  %0A%0A Order Profile:- {order_profile_url}',
                    customer_phone=order.payment.phone_number,
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

    return JsonResponse({'status': 'done'})

@csrf_exempt
@api_view(['GET', 'POST'])
def ccavenue_hook(request):
    try:
        gateway = PaymentGateway.objects.get(name='CCAvenue')
        working_key = gateway.working_key
        plain_text = request.POST.get('encResp')
        
        decResp = decrypt(plain_text, working_key)
        payment_data = {}
        decResp = decResp.split('&')
        for data in decResp:
            key, value = data.split('=')
            payment_data[key] = value

        if payment_data['order_status'] == 'Success':
            # payment is success
            order_id = payment_data['order_id']
            ccavenue_payment = CCAvenuePayment.objects.filter(uu_id=order_id).first()
            
            if ccavenue_payment:
                payment = ccavenue_payment.payment
                order = payment.order
                payment.payment_method = 'Gateway'
                payment.status = 'Success'
                payment.time=localtime(timezone.now())
                payment.ccavenuepayment.tracking_id = payment_data['tracking_id']
                payment.ccavenuepayment.bank_ref_no = payment_data['bank_ref_no']
                payment.ccavenuepayment.save()
                payment.save()


                seat = order.seat
                seat.is_vacent = False
                seat.save()
                order_status_url = reverse("theatre:order-status", args=[payment.order.pk])
                order_status_url = f"https://www.scan2food.com{order_status_url}"
                cusotmer_message = f"🎉 *Order Confirmed!* 🍿🥤%0A%0AThank you for your order, and welcome to *{seat.row.hall.theatre.name}*! 🎬✨%0A%0A🪑 *Your Seat:* {seat.row.hall.name}, {seat.name} %0A📍 *Track your order:* {order_status_url}%0A%0ASit back, relax, and enjoy your movie without missing a single scene!%0A%0A🚀 We'll deliver your food and drinks to your seat shortly.%0A%0Aℹ️ For assistance, contact our theatre staff at {seat.row.hall.theatre.query_number} 📞.%0A%0A⚠️ Please do not reply to this message or call this number.%0A%0AEnjoy the show! 🍿🎟️%0A%0A— *Team Scan2Food* 🚀"

                order_profile_url = reverse("theatre:order-profile", args=[order.pk])
                order_profile_url = f"https://www.scan2food.com{order_profile_url}"

                group = seat.row.hall.theatre.group

                # update websocket
                update_websocket(
                    theatre_id=seat.row.hall.theatre.id,
                    seat_id=seat.id,
                    is_vacent=seat.is_vacent,
                    payment_panding=False,
                    seat_name=f"{seat.row.hall.name} | {seat.name}",
                    message=f'New Order Come From Seat {seat.row.hall.name} | {seat.name}  %0A%0A Order Profile:- {order_profile_url}',
                    customer_phone=order.payment.phone_number,
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

    except:
        pass
    return JsonResponse({'status': 'done'})

@csrf_exempt
@api_view(['GET', 'POST'])
def get_payu_form_details(request, pk):
    order = Order.objects.get(pk=pk)
    payment = order.payment
    try:
        if payment.gateway == 'PayU':
            gateway_detail = PaymentGateway.objects.get(name="PayU")
            key = gateway_detail.gateway_key
            # client_secret = gateway_detail.gateway_secret
            salt = gateway_detail.gateway_salt

            theatre_mail = order.seat.row.hall.theatre.name
            theatre_mail = theatre_mail.replace(" ", ".")

            try:
                uu_id = payment.payupayment.uu_id

            except:
                uu_id = str(uuid4())

                while True:
                    sameuuid = PayuPayment.objects.filter(uu_id=uu_id).first()
                    if sameuuid == None:
                        break
                    else:
                        continue
                
                PayuPayment.objects.create(
                    payment = payment,
                    uu_id = uu_id,
                    order_id = f"temp-{uu_id}"
                )

            return_data = {}

            return_url = request.build_absolute_uri(reverse('theatre:payu-payment-callback', args=[order.pk]))
            return_url = return_url.replace('http', 'https')

            parmas = {
                'key': key,
                'txnid': uu_id,
                'productinfo': f"{order.seat.row.hall.theatre.name} {order.seat.row.hall.name} {order.seat.name}",
                'amount': f"{order.payment.amount}",
                'email': f"{theatre_mail}@scan2food.com",
                'firstname': order.seat.row.hall.theatre.name,
                'surl': return_url,
                'furl': return_url,
                'phone': f'{order.payment.phone_number}',
            }

            return_data = parmas
            hash = generate_hash(parmas, salt)
            return_data['hash'] = hash

            return JsonResponse(return_data)

    except:
        return JsonResponse({'status': 'error', 'message': 'Something went wrong'})
    

@api_view(['GET'])
def get_all_images(request):
    return_data = {}
    # get food images folder
    food_folder = os.path.join(settings.MEDIA_ROOT, 'food_images')

    # get all the images
    if os.path.exists(food_folder):
        images = [
            (settings.MEDIA_URL + 'food_images/' + image) for image in os.listdir(food_folder)
        ]
    else:
        images = []
    return_data['images'] = images

    return JsonResponse(return_data)

@api_view(['POST'])
@login_required
def upload_food_image(request):
    data = request.data

    food_id = data.get('food_id')
    image_url = data.get('image_url')
    theatre = request.user.userprofile.theatre
    food_item = FoodItem.objects.get(pk=food_id)

    if food_item.catogary.theatre == theatre:
        image_path = image_url.split(settings.MEDIA_URL)[1]
        # image_path = os.path.join(settings.MEDIA_ROOT, image_path)
        
        food_item.food_image = image_path
        food_item.save()
        return JsonResponse({'message': 'Image Uploaded'})

    else:
        return JsonResponse({'message': 'Permission Denied'})


@login_required
def get_phone_number_by_order_id(request, pk):
    return_data = {"phone_number": "Not provided", "status": False}
    try:
        order = Order.objects.get(pk=pk)
        phone_number = order.payment.phone_number
        if phone_number == "":
            pass
        else:
            return_data['phone_number'] = phone_number
            return_data['status'] = True
    except:
        pass

    return JsonResponse(return_data)

@login_required
def get_all_theatres(request):
    cache_key = "all_theatres"
    cache_data = cache.get(cache_key)
    if cache_data:
        return JsonResponse(cache_data)
    else:

        all_theatres = []
        theatres = Theatre.objects.all()
        for theatre in theatres:
            append_data = {'theatre_id': theatre.pk, 'name': theatre.name}
            all_theatres.append(append_data)

        return_data = {'all_theatres': all_theatres}
        cache.set(cache_key, return_data, 60 * 60 * 1) # cache for 1 Day

    return JsonResponse(return_data) 

def is_order_viewed(request, pk):
    seat = Seat.objects.get(pk=pk)
    order = seat.order_set.filter(payment__status='Success').last()
    
    if order.is_shown == False:
        order.is_shown = True
        order.save()
        # update the websocket
        update_websocket(
            msg_typ='order_seen',
            seat_id=order.seat.id,
            theatre_id=order.seat.row.hall.theatre.pk,
            order_id=order.pk
        )
    return JsonResponse({'status': 'done'})

@login_required
def update_bulk_status(request):
    permission = Permission.objects.get(codename="view_order")
    if request.user.groups.first().permissions.filter(id=permission.id).exists():
        theatre = request.user.userprofile.theatre
        # is user is from the same theatre
        if request.user.userprofile.theatre != theatre:
            return JsonResponse({'status': 'Permission Denied'})
        else:
            made_by = request.GET.get('made_by')
            status = request.GET.get('status')
            cache_key = f'theatre_menu_{theatre.pk}'
            cache.delete(cache_key)

            if made_by == 'all':

                if status == 'activate':
                    # deactivate the qr service
                    return JsonResponse({'message': 'Activate Your QR Service from Settings Page !'})
                else:
                    return JsonResponse({'message': 'QR Service is Deactivated'})

            all_items = FoodItem.objects.filter(catogary__theatre=theatre, unavailable_by='auto', made_by=made_by)

            for item in all_items:

                if status == 'activate':
                    item.is_available = True
                else:
                    item.is_available = False
                item.save()
            
            if status == 'activate':
                return JsonResponse({'message': f'There are {all_items.count()} Items are Activated'})

            else:
                return JsonResponse({'message': f'There are {all_items.count()} Items are Deactivated'})
    else:
        return JsonResponse({'status': 'Permission Denied'})
    

def generate_otp(request, pk, regenerate):
    order = Order.objects.get(pk=pk)

    if order.payment.status == 'Success':
        if order.refund_otp != "":
            message = "OTP is already sent to the theatre's OTP number! "
            status = "Not send !"
        
        if regenerate == "resend" or order.refund_otp == "" or order.refund_otp == None:
            if order.otp_timing == "" or order.otp_timing == None:
                otp_timing = localtime(timezone.now())
                
            else:
                current_time = localtime(timezone.now())
                otp_time = timezone.localtime(order.otp_timing)

                if current_time - otp_time > timedelta(minutes=5):
                    otp_timing = localtime(timezone.now())
                else:
                    return JsonResponse({'message': 'OTP is already sent to the user and Nexe opt will sent after 5 min !', 'status': 'error'})

            otp = str(randint(1000, 9999))
            order.otp_timing = otp_timing
            order.refund_otp = otp
            order.save()
            # send otp to the theatre otp number if otp number is not provided then send to the main number.
            theatre = order.seat.row.hall.theatre
            if theatre.otp_phone_number:
                phone_number = theatre.otp_phone_number
            else:
                phone_number = theatre.phone_number


            order_profile_url = reverse("theatre:order-profile", args=[order.pk])
            order_profile_url = f"https://www.scan2food.com{order_profile_url}"

            cusotmer_message = otp
            # update websocket
            update_websocket(
                message='otp',
                customer_phone=phone_number,
                customer_message=cusotmer_message,
                theatre_name=order.seat.row.hall.theatre.name,
                msg_typ="generate-otp",
                order_id=order.pk
            )
            message = f"OTP is sent to {theatre.otp_person_name} on {theatre.otp_phone_number if theatre.otp_phone_number else theatre.phone_number}"
            status = "sent"

        return JsonResponse({'message': message, 'status': status})
    else:
        return JsonResponse({'message': 'Payment is not successful', 'status': 'error'})

@login_required
def generate_update_otp(request):
    permission = Permission.objects.get(codename="add_fooditem")
    if request.user.groups.first().permissions.filter(id=permission.id).exists():
        theatre = request.user.userprofile.theatre
        if theatre.otp_time is None or theatre.otp_time == "":
            otp_timing = localtime(timezone.now())
        else:
            current_time = localtime(timezone.now())
            otp_time = timezone.localtime(theatre.otp_time)

            if current_time - otp_time > timedelta(minutes=5):
                otp_timing = localtime(timezone.now())
            else:
                return JsonResponse({'message': f'OTP is sent to {theatre.otp_person_name} on {theatre.otp_phone_number if theatre.otp_phone_number else theatre.phone_number} and Next OTP will be sent after 5 min !', 'status': 'error'})
            
        otp = randint(1000, 9999)
        theatre.otp = otp
        theatre.otp_time = otp_timing
        theatre.save()
        

        phone_number = theatre.otp_phone_number if theatre.otp_phone_number else theatre.phone_number
        cusotmer_message = f"🔐 OTP Number Update Require OTP %0A%0AAn OTP has been generated for updating the theatre details. Please verify using the OTP provided below. ✅%0A%0A🔢 OTP for Update: {otp} %0A%0ANeed help? Contact Scan2Food support.%0A%0A— Team Scan2Food 🔒"

        update_websocket(
            message='otp',
            customer_phone=phone_number,
            customer_message=cusotmer_message,
            theatre_name=theatre.name,
            msg_typ="generate-otp",
            )

        message = f"OTP is sent to {theatre.otp_person_name} on {theatre.otp_phone_number if theatre.otp_phone_number else theatre.phone_number}"
        status = "sent"

        return JsonResponse({'message': message, 'status': status})

    
    else:
        return JsonResponse({'status': 'Permission Denied'})

@sync_to_async
def serialize_order(order):
    theatre = order.seat.row.hall.theatre
    return {
        'id': order.id,
        'payment_time': localtime(order.payment.time).strftime("%d-%b-%Y|%I:%M %p"),
        'delivery_time': localtime(order.delivery_time).strftime("%d-%b-%Y|%I:%M %p"),
        'order_amount': order.order_amount(),
        'total_amount': order.payment.amount,
        'theatre_id': theatre.id,
        'theatre_name': theatre.name,
        'quantity': order.items.count(),
        'seat': f"{order.seat.row.hall.name}, {order.seat.name}",
        'payment_status': getattr(order.payment, 'status', None),
        'view_status': order.is_shown,
        'taken_by': order.who_taken(),
        'deliverd_by': order.who_deliverd(),
        'items': order.get_items(),
    }

async def sse_orders_stream(request):
    """
    Streams each order individually over SSE.
    """

    # fetch all orders (wrapped in sync_to_async)
    orders = await sync_to_async(get_all_orders)(request)

    async def event_stream():
        for order in orders:
            serialized = await serialize_order(order)
            payload = json.dumps(serialized)
            yield f"data: {payload}\n\n"
        

    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )

    response["Access-Control-Allow-Origin"] = "*"  # Allow all for testing
    response["Cache-Control"] = "no-cache"
    return response

def live_orders(request):
    return_data = {}

    cache_key = 'live-orders'
    cache_data = cache.get(cache_key)
    if cache_data:
        cache.delete(cache_key)
        return JsonResponse(cache_data, safe=False)
    
    all_running_orders = Order.objects.filter(
        # payment__status='Success',
        delivery_time__isnull=True,
        seat__is_vacent=False
        ).filter(
            Q(payment__payment_method='Cash') | 
            Q(~Q(payment__payment_method='Cash'), payment__status='Success')
        )
    all_running_orders = all_running_orders.order_by('payment__time')

    for order in all_running_orders:
        try:
            food_item_with_max_time = (
                FoodItem.objects
                .filter(orderitems__order=order)
                .order_by('-max_time')
                .first()
            )

            seat = order.seat
            seat_data = {
                'seat_id': seat.pk,
                'seat_name': seat.name,
                'hall_name': seat.row.hall.name,
                'is_vacent': seat.is_vacent,
                'theatre_id': seat.row.hall.theatre.pk,
                'theatre_name': seat.row.hall.theatre.name,
                'payment_method': order.payment.payment_method,
                'payment_status': order.payment.status,
                'is_shown': order.is_shown,
                'payment_time': localtime(order.payment.time).strftime("%d-%b-%Y|%I:%M %p"),
                'amount': order.full_payment(),
                'order_id': order.id,
                'max_time': food_item_with_max_time.max_time,
                'min_time': 5
            }

            return_data[f'seat-id-{seat.pk}'] = seat_data
        except:
            pass
        
    cache.set(cache_key, return_data, timeout=60 * 5)  # Cache for 5 minutes (300 sec)

    return JsonResponse(return_data)

def get_last_payout(request):
    try:
        last_payout = PayOutLogs.objects.last()
        payments = [{'payment_id': payment.id, 'order_id': payment.order.pk, 'theatre_amount': payment.order.order_amount(), 'total_amount': payment.amount} for payment in last_payout.payment_set.all()]
        return_data = {
            'start_time': localtime(last_payout.start_time).strftime("%d-%b-%Y | %I:%M %p"),
            'end_time': localtime(last_payout.end_time).strftime("%d-%b-%Y | %I:%M %p"),
            'end_date': localtime(last_payout.end_time).strftime("%d-%b-%Y"),
            'generated_time': localtime(last_payout.generated_time).strftime("%d-%b-%Y | %I:%M %p"),
            'amount': last_payout.amount,
            'is_settled': last_payout.is_settled,
            'payments': payments
        }
    
    except Exception as e:
        return_data = {'error': str(e)}

    return JsonResponse(return_data)

@login_required
def refund_query_count(request):
    user = request.GET.get('user', "")
    # FOR ADMIN
    if user == "admin":
        cache_key = 'all-refund-query-count'
        cache_data = cache.get(cache_key)
        if cache_data:
            return JsonResponse(cache_data)
        else:
            refund_queries = OrderRefundRequest.objects.filter(resolve_status=False).count()
            return_data = {'count': refund_queries}
            # UPDATE THE CACHE 
            cache.set(cache_key, return_data, timeout=60 * 30)  # Cache for 30 minutes (1800 sec)
            return JsonResponse(return_data)
    
    # FOR NORMAL USER
    else:
        theatre = request.user.userprofile.theatre
        cache_key = f'refund-query-id-{theatre.id}'
        cache_data = cache.get(cache_key)
        if cache_data:
            return JsonResponse(cache_data)

        else:
            refund_queries = OrderRefundRequest.objects.filter(order__seat__row__hall__theatre=theatre, resolve_status=False).count()
            return_data = {'count': refund_queries}
            # UPDATE TEH CACHE 
            cache.set(cache_key, return_data, timeout=60 * 30)  # Cache
            return JsonResponse(return_data)

@login_required
def update_refund_query_status(request, pk):
    refund_query = OrderRefundRequest.objects.get(pk=pk)
    if refund_query.resolve_status == False:
        refund_query.resolve_status = True
        refund_query.save()
        # CLEAR THE CACHE
        cache_key = f'refund-query-id-{refund_query.order.seat.row.hall.theatre.id}'
        cache.delete(cache_key)
        cache_key = 'all-refund-query-count'
        cache.delete(cache_key)
        return JsonResponse({'status': 'success', 'message': 'Refund query marked as resolved'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Refund query is already resolved'})

@login_required
def get_order_id_by_phone_no(request, phone_number):
    return_data = {'order_id': None, 'status': 'error'}
    try:
        payment = Payment.objects.filter(phone_number=phone_number, status='Success').last()
        if payment:
            return_data['order_id'] = payment.order.pk
            return_data['status'] = 'success'
    except:
        pass
    
    return JsonResponse(return_data)

# @login_required
# def update_user_profile(request, pk):
#     if request.user.groups.filter(name='admin').exists():
#         try:
#             user_profile = UserProfile.objects.get(pk=pk)
#         except:
#             return {'message': 'You are not allowed'}
#         return JsonResponse({'status': 'admin'})
#     else:
#         return JsonResponse({'status': 'koi or ha...'})