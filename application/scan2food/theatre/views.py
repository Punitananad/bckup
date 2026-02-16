from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib import messages
from .decorator import login_required
from .models import *
import json
from django.contrib.auth.models import Permission, User, Group
from .form import FoodItemForm, UpdateTheatreDetil, AddTax, SimpleUserProfileForm, SignUp, FoodCategoryForm, OtpPhoneNumberForm
from django.utils import timezone
from django.utils.timezone import localtime
from datetime import datetime, timedelta, time
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, Http404, JsonResponse
# send data to websocket
from .update_websocket import update_websocket, send_whatsapp_template

import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from django.db.models import Sum
import requests
from requests.auth import HTTPBasicAuth
from adminPortal.models import Detail, PayOutLogs, PaymentGateway, Commission
import os
from django.urls import reverse

# imports for cahsfree gateways
from cashfree_pg.models.create_order_request import CreateOrderRequest
from cashfree_pg.models.order_create_refund_request import OrderCreateRefundRequest
from cashfree_pg.api_client import Cashfree
from cashfree_pg.models.customer_details import CustomerDetails
from cashfree_pg.models.order_meta import OrderMeta
# ends for cashfree payments ends 

# add caching
from django.core.cache import cache


# imports for phonepe gateways
from uuid import uuid4
from phonepe.sdk.pg.payments.v2.standard_checkout_client import StandardCheckoutClient
from phonepe.sdk.pg.payments.v2.models.request.standard_checkout_pay_request import StandardCheckoutPayRequest
from phonepe.sdk.pg.env import Env
from phonepe.sdk.pg.common.models.request.refund_request import RefundRequest
# end for phonepe gateways

# imports for CCAvenue gateways
from Crypto.Cipher import AES
from hashlib import md5
import base64


# Helper function to check permissions for both superusers and regular users
def user_has_permission(user, permission_codename):
    """
    Check if user has permission. Superusers always have all permissions.
    Regular users need to have the permission in their group.
    """
    # Superusers have all permissions
    if user.is_superuser:
        return True
    
    # Check if user has groups and the permission
    user_group = user.groups.first()
    if user_group:
        try:
            permission = Permission.objects.get(codename=permission_codename)
            return user_group.permissions.filter(id=permission.id).exists()
        except Permission.DoesNotExist:
            return False
    
    return False


# imports for PayU gateways
import hashlib

import pandas as pd


def pad(data):
    length = 16 - (len(data) % 16)
    return data + chr(length) * length

def unpad(data):
    return data[:-ord(data[-1])]

def encrypt(plainText, workingKey):
    iv = bytes([i for i in range(16)])
    encDigest = md5(workingKey.encode('utf-8')).digest()
    plainText = pad(plainText)
    cipher = AES.new(encDigest, AES.MODE_CBC, iv)
    encryptedText = cipher.encrypt(plainText.encode('utf-8'))
    return encryptedText.hex()  # or use base64.b64encode(encryptedText).decode()

def decrypt(cipherText, workingKey):
    iv = bytes([i for i in range(16)])
    decDigest = md5(workingKey.encode('utf-8')).digest()
    encryptedBytes = bytes.fromhex(cipherText)
    cipher = AES.new(decDigest, AES.MODE_CBC, iv)
    decryptedText = cipher.decrypt(encryptedBytes).decode('utf-8')
    return unpad(decryptedText)

# ends for CCAvenue gateways

from django.views.decorators.cache import never_cache
from django.db.models import Q



# Create your views here.
@login_required
def index(request):
    theatre = request.user.userprofile.theatre
    current_year = localtime(timezone.now()).year
    return render(request, 'theatre/index.html', {"theatre": theatre, 'current_year': current_year})

@login_required
def seat_view(request):
    theatre = request.user.userprofile.theatre
    return render(request, 'theatre/all_seats.html', {"theatre": theatre})
    # return redirect('theatre:live-orders')

@login_required
def live_orders(request):
    theatre = request.user.userprofile.theatre
    context = {'theatre': theatre}
    return render(request, 'theatre/live-orders.html', context)

@login_required
def add_hall(request):
    if user_has_permission(request.user, "add_hall"):
        if request.method == 'POST':
            new_hall_name = request.POST['hall-name']
            theatre = request.user.userprofile.theatre
            old_hall = Hall.objects.filter(theatre=theatre, name=new_hall_name)
            if old_hall:
                messages.error(request, f'Hall With Name: {new_hall_name} is already there')

            else:
                new_hall = Hall(name=new_hall_name, theatre=theatre)
                new_hall.save()
                messages.success(request, 'New Hall is Generated')

            return redirect('theatre:add-hall')
        
        all_hall = request.user.userprofile.theatre.hall_set.all()
        return render(request, 'theatre/add-hall.html', {"all_hall": all_hall})
    else:
        return HttpResponse('Permissio Denied')

@login_required
def add_seat_to_hall(request, pk):
    if user_has_permission(request.user, "add_seat"):
    # if request.user.groups.filter(name='admin').exists():
        try:
            hall = Hall.objects.get(pk=pk)
            if request.method == 'POST':
                tablesData = request.POST['send-data']
                tablesData = json.loads(tablesData)
                for row in tablesData:
                    old_row = Row.objects.filter(name=row, hall=hall).first()
                    if old_row:
                        new_row = old_row
                    else:
                        new_row = Row.objects.create(name=row, hall=hall)

                    for seat in tablesData[row]:
                        old_seat = Seat.objects.filter(name=seat, row=new_row)
                        if old_seat:
                            pass
                        else:
                            Seat.objects.create(name=seat, row=new_row)
                
                messages.success(request, 'All New Seats Are Added Successfully to the Theatre')
                return redirect('theatre:add-hall')
        
        except:
            raise Http404('page not found')
        
        else:
            return render(request, 'theatre/add-seat-to-hall.html', {'hall': hall})

    else:
        return HttpResponse("Permission Denied")

@login_required
def theatre_setting(request):
    return render(request, 'theatre/settings.html')

@login_required
def add_menu(request):
    if user_has_permission(request.user, "add_fooditem"):
        # add Menue to this Theatre
        theatre = request.user.userprofile.theatre
        food_categories = FoodCategory.objects.filter(theatre=theatre)
        form = FoodItemForm(theatre=theatre)
        category_form = FoodCategoryForm()
        return render(request, 'theatre/add-menu.html', {"food_categories": food_categories, "form": form, "category_form": category_form})
    else:
        return HttpResponse('Permissio Denied')

@login_required
def add_category(request):
    if user_has_permission(request.user, "add_fooditem"):
        # add catogary to only this Theatre
        if request.method == 'POST':
            form = FoodCategoryForm(request.POST)
            if form.is_valid():
                food_category = form.save(commit=False)
                food_category.theatre = request.user.userprofile.theatre
                food_category.save()
                messages.success(request, f"New Food catogary with name: {food_category.name} is added in your theatre")
            
            return redirect('theatre:add-menu')
    
    else:
        return HttpResponse('Permissio Denied')
    
@login_required
def add_food_item(request, pk=None):
    if user_has_permission(request.user, "add_fooditem"):
        theatre = request.user.userprofile.theatre
        if request.method == 'POST':
            if pk:
                food_item = get_object_or_404(FoodItem, pk=pk)
            
                form = FoodItemForm(request.POST, instance=food_item, theatre=theatre)

            else:
                form = FoodItemForm(request.POST, theatre=theatre)
            
            if form.is_valid():
                form.save()
                cache_key = f'theatre_menu_{theatre.pk}'
                cache.delete(cache_key)
            return redirect("theatre:add-menu")
        else:
            # GET request - redirect to add-menu page where the modal form is
            return redirect("theatre:add-menu")
    else:
        return HttpResponse('Permission Denied')

@login_required
def upload_menu(request, pk=None):
    if request.method == 'POST':
        excel_file = request.FILES.get("file")
        if not excel_file:
            return JsonResponse({"error": "No file uploaded"}, status=400)

        if not excel_file.name.endswith((".xls", ".xlsx")):
            return JsonResponse({"error": "Invalid file type"}, status=400)

        try:
            categories = FoodCategory.objects.filter(theatre__pk=request.user.userprofile.theatre.pk).all()
            categories.delete()

            df = pd.read_excel(excel_file)

            all_records = df.groupby("Category").apply(lambda x: x.drop(columns="Category").to_dict(orient="records")).to_dict()

            for record in all_records:
                category = FoodCategory.objects.filter(theatre=request.user.userprofile.theatre, name=record).first()

                if not category:
                    category = FoodCategory.objects.create(
                        theatre=request.user.userprofile.theatre,
                        name=record
                    )

                for item in all_records[record]:
                    FoodItem.objects.create(
                        catogary=category,
                        name=item['Item Name'],
                        description=item.get('Description', ''),
                        price=item['Price'],
                        priority_number=item.get('priority', 1),
                        min_time=item.get('min_time', 5),
                        max_time=item.get('max_time', 30),
                    )
                    
            messages.success(request, 'Menu Uploaded Successfully')
            return redirect('theatre:add-menu')

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
    return render(request, 'theatre/upload-menu.html')

@login_required
def change_availablity(request, pk):
    if user_has_permission(request.user, "add_fooditem"):
        try:
            food_item = FoodItem.objects.get(pk=pk)
            if food_item.catogary.theatre == request.user.userprofile.theatre:
                if food_item.is_available:
                    food_item.unavailable_by = 'manual'
                    food_item.is_available = False
                    messages.error(request, f'{food_item.name} is Unavailable from Now !')

                else:
                    food_item.unavailable_by = 'auto'
                    food_item.is_available = True
                    messages.success(request, f'{food_item.name} is Available from Now !')
                
                food_item.save()
                cache_key = f'theatre_menu_{food_item.catogary.theatre.pk}'
                cache.delete(cache_key)
                return redirect('theatre:add-menu')
            else:
                HttpResponse('Permission Denied')

        except:
            raise Http404('page not found')
    else:
        HttpResponse('Permission Denied')

@login_required
def delete_food_item(request):
    if user_has_permission(request.user, "add_fooditem"):
        if request.method == 'POST':
            pk = request.POST.get('pk')
            food_item = FoodItem.objects.get(pk=pk)
            if request.user.userprofile.theatre == food_item.catogary.theatre:
                if food_item.food_image != 'default_food_img.png':
                    if os.path.isfile(food_item.food_image.path):
                        os.remove(food_item.food_image.path)

                food_item.delete()

                return redirect('theatre:add-menu')
            else:
                return HttpResponse('Permission Denied')
    else:
        return HttpResponse('Permission Denied')


@login_required
def delete_food_category(request, pk):
    if user_has_permission(request.user, "add_fooditem"):
        if request.method == 'POST':
            try:
                food_category = get_object_or_404(FoodCategory, pk=pk)
                if food_category:
                    if food_category.theatre == request.user.userprofile.theatre:
                        if food_category.category_image != 'default_food_img.png':
                            if os.path.isfile(food_category.category_image.path):
                                os.remove(food_category.category_image.path)
                                
                        food_category.delete()
                        messages.success(request, 'Category Has Been Removed Successfully')
                        return redirect('theatre:add-menu')
                    else:
                        messages.error(request, f"You Haven't Permission to delete this Cagetory")
                else:
                    messages.error(request, 'Category is already removed !')
            except:
                raise Http404('page not found')
            
    else:
        return HttpResponse('Permission Denied')
    
@login_required
def theatre_detail(request):
    if user_has_permission(request.user, "change_theatre"):
        current_user = request.user
        theatre = current_user.userprofile.theatre
        if request.method == 'POST':
            form = UpdateTheatreDetil(request.POST, instance=theatre)
            if form.is_valid():
                form.save()
                messages.success(request, 'Detail Updated Successfully !')
                return redirect('theatre:theatre-detail')
            
        form = UpdateTheatreDetil(instance=theatre)
        return render(request, 'theatre/theatre-detail.html', {'form': form})
    else:
        return HttpResponse('Permission Denied')

@login_required
def otp_details(request):
    if user_has_permission(request.user, "change_theatre"):
        theatre = request.user.userprofile.theatre
        old_otp = theatre.otp
        form = OtpPhoneNumberForm(instance=theatre)
        if request.method == 'POST':
            form = OtpPhoneNumberForm(request.POST, instance=theatre)
            if form.is_valid():
                
                form.save(commit=False)
                
                if form.cleaned_data['otp'] == old_otp:
                    theatre.otp_phone_number = form.cleaned_data['otp_phone_number']
                    theatre.otp_person_name = form.cleaned_data['otp_person_name']
                    theatre.otp = ""
                    theatre.otp_time = None
                    theatre.save()
                    messages.success(request, 'OTP Phone Number Details Updated Successfully !')
                else:
                    messages.error(request, 'Invalid OTP !')
                return redirect('theatre:otp-details')
            
            else:
                messages.error(request, 'Invalid Form Submission !')
                return redirect('theatre:otp-details')
            
        return render(request, 'theatre/otp-details.html', {'form': form, 'theatre': theatre})
    else:
        return HttpResponse('Permission Denied')

@login_required
def update_scaning_service(request):
    if user_has_permission(request.user, "change_theatre"):
        theatre = request.user.userprofile.theatre
        theatre_detail = theatre.detail
        
        if theatre_detail.scaning_service:
            theatre_detail.break_start_time = localtime(timezone.now()).time()
            theatre_detail.scaning_service = False
            whatsapp_message = "Deactivated"
            msg = 'Scaning food service is deactivated from now it will automatically start tomorrow at 8:00 AM'
            messages.success(request, msg)

        else:
            theatre_detail.break_start_time = None
            theatre_detail.scaning_service = True
            whatsapp_message = "Activated"
            msg = 'Scaning food service are Activated Again'
            messages.success(request, msg)
        
        theatre_detail.save()

        if theatre.otp_phone_number:
            phone_number = theatre.otp_phone_number
        else:
            phone_number = theatre.phone_number

        # send live data to websocket.
        update_websocket(
            bg_type="bg-success", 
            customer_phone=phone_number, 
            customer_message=whatsapp_message,
            group=theatre.group,
            msg_typ='scaning-service-status',
            message=msg
            )

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


    else:
        return HttpResponse('Permission Denied')

@login_required
def add_tax(request):
    if user_has_permission(request.user, "change_theatre"):
        if request.method == 'POST':
            form = AddTax(request.POST)
            if form.is_valid():
                theatre = request.user.userprofile.theatre
                new_tax = form.save(commit=False)
                new_tax.theatre = theatre
                new_tax.save() 
                messages.success(request, 'New Tax is Added To Your Theatre')
                
                return redirect('theatre:add-tax')
        all_tax = request.user.userprofile.theatre.tax_set.all()
        form = AddTax()
        return render(request, 'theatre/add-tax.html', {'form': form, "all_tax": all_tax})

    else:
        return HttpResponse('Permission Denied')
    
@login_required
def remove_tax(request, pk):
    if user_has_permission(request.user, "change_theatre"):
        try:
            tax = get_object_or_404(Tax, pk=pk)
            if tax:
                tax_name = tax.name
                if request.user.userprofile.theatre == tax.theatre:
                    tax.delete()
                    messages.success(request, f'Tax:- {tax_name} Has Been Removed From Your Theatre')
                else:
                    messages.error(request, 'you have right access to delete this')
            else:
                messages.error(request, 'This Tax is no more available')
            return redirect('theatre:add-tax')
        except:
            raise Http404('page not found')
        
    else:
        return HttpResponse('Permission Denied')

@login_required
def payout_payments(request, pk):
    if user_has_permission(request.user, "change_theatre"):
        try:
            payout = PayOutLogs.objects.get(pk=pk)
            if payout.theatre == request.user.userprofile.theatre:
                payments = payout.payment_set.order_by('-time')
                return render(request, 'theatre/payout-payments.html', {"payout": payout, "payments": payments})
            else:
                return HttpResponse('Permission Denied')
        except:
            raise Http404('page not found')
        
    else:
        return HttpResponse('Permission Denied')

@login_required
def all_payouts(request):
    if user_has_permission(request.user, "change_theatre"):
        theatre = request.user.userprofile.theatre
        all_payouts = theatre.payoutlogs_set.all().order_by('-start_time')
        last_payout = all_payouts.first()
        if last_payout == None:
            last_payout = {'amount': 0}

        date_range = request.GET.get('daterange', "")
        if date_range == "":
            start_date = localtime(timezone.now()).date()
            end_date = localtime(timezone.now()).date()
        else:
            try:
                start_date = date_range.split(" - ")[0]
                end_date = date_range.split(" - ")[1]

                start_date = datetime.strptime(start_date, "%d/%b/%Y").date()
                end_date = datetime.strptime(end_date, "%d/%b/%Y").date()
            except:
                start_date = localtime(timezone.now()).date()
                end_date = localtime(timezone.now()).date()

        all_payouts = all_payouts.filter(start_time__date__range=(start_date, end_date))

        pending_payments = Payment.objects.filter(order__seat__row__hall__theatre=theatre, is_settled=False, status='Success', payment_method='Gateway')
        if pending_payments.count() == 0:
            current_balance = 0
        else:
            current_balance = sum(payment.order.full_payment() - payment.settlement for payment in pending_payments)

        paginator = Paginator(all_payouts, 25)  # Show 25 items per page.

        page_number = request.GET.get('page')
        if page_number == None:
            page_number = 1

        all_payouts = paginator.get_page(page_number)


        context = {
            "theatre": theatre,
            "all_payouts": all_payouts,
            "last_payout": last_payout,
            "current_balance": current_balance,
            "start_date": start_date,
            "end_date": end_date
        }
        return render(request, 'theatre/all-payouts.html', context)

    else:
        return HttpResponse('Permission Denied')

@login_required
def all_orders(request):
    if user_has_permission(request.user, "view_order"):
        return render(request, 'theatre/all-orders.html')
    
    else:
        return HttpResponse('Permission Denied')

@login_required
def all_payments(request):
    if user_has_permission(request.user, "view_order"):
        theatre = request.user.userprofile.theatre
        date_range = request.GET.get('daterange', "")
        if date_range == "":
            start_date = localtime(timezone.now()).date()
            end_date = localtime(timezone.now()).date()
        else:
            try:
                start_date = date_range.split(" - ")[0]
                end_date = date_range.split(" - ")[1]

                start_date = datetime.strptime(start_date, "%d/%b/%Y").date()
                end_date = datetime.strptime(end_date, "%d/%b/%Y").date()
            except:
                start_date = localtime(timezone.now()).date()
                end_date = localtime(timezone.now()).date()

        all_payments = Payment.objects.filter(status='Success',order__seat__row__hall__theatre=theatre, time__date__range=(start_date, end_date))
        all_payments = all_payments.order_by('-time')
        paginator = Paginator(all_payments, 10)  # Show 10 items per page.

        page_number = request.GET.get('page')
        if page_number == None:
            page_number = 1

        all_payments = paginator.get_page(page_number)

        return render(request, 'theatre/all-payments.html', {'all_payments': all_payments, "start_date": start_date, "end_date": end_date})
    else:
        return HttpResponse('Permission Denied')
    
@login_required
def all_reviews(request):
    if user_has_permission(request.user, "view_order"):
        theatre = request.user.userprofile.theatre
        date_range = request.GET.get('daterange', "")
        if date_range == "":
            start_date = localtime(timezone.now()).date()
            end_date = localtime(timezone.now()).date()
        else:
            try:
                start_date = date_range.split(" - ")[0]
                end_date = date_range.split(" - ")[1]

                start_date = datetime.strptime(start_date, "%d/%b/%Y").date()
                end_date = datetime.strptime(end_date, "%d/%b/%Y").date()
            except:
                start_date = localtime(timezone.now()).date()
                end_date = localtime(timezone.now()).date()
        
        all_reviews = Order.objects.filter(review_done=True,seat__row__hall__theatre=theatre, payment__time__date__range=(start_date, end_date))

        rating = all_reviews.aggregate(total=Sum('rating'))['total']
        order_count = all_reviews.count()
        total_rating = order_count * 5

        all_reviews = all_reviews.order_by('-payment__time')
        paginator = Paginator(all_reviews, 10)  # Show 10 items per page.

        page_number = request.GET.get('page')
        if page_number == None:
            page_number = 1

        all_reviews = paginator.get_page(page_number)

        return render(request, 'theatre/all-reviews.html', {'all_reviews': all_reviews, "start_date": start_date, "end_date": end_date, "rating": rating, "order_count": order_count, "total_rating": total_rating})

    else:
        return HttpResponse('Permission Denied')

@login_required
def show_order_profile(request, pk):
    if user_has_permission(request.user, "view_order"):
        try:
            order = Order.objects.get(pk=pk)
            if request.user.userprofile.theatre == order.seat.row.hall.theatre:
                theatre = request.user.userprofile.theatre
                return render(request, 'theatre/order-profile.html', {"order_id": order.id, 'theatre': theatre})
            else:
                return HttpResponse('Permission Denied')
        except:
            raise Http404('page not found')

    else:
        return HttpResponse('Permission Denied')

def generate_cash_order(request, pk):
    try:
        order = Order.objects.get(pk=pk)
        payment = order.payment
        if payment.status == 'Created':
            seat = order.seat
            seat.is_vacent = False
            seat.save()
            payment.payment_method = 'Cash'
            payment.status = 'Created'
            payment.save()

            # UPDATE THE SEAT STATUS VIA WEBSOCKET
            update_websocket(
                theatre_id=order.seat.row.hall.theatre.id,
                theatre_name=order.seat.row.hall.theatre.name,
                order_id=order.id,
                seat_id=order.seat.id,
                is_vacent=order.seat.is_vacent,
                payment_panding=True,
                seat_name=f"{seat.row.hall.name} | {seat.name}",
                bg_type='bg-warning',
                message=f'New Order Come From {order.seat.row.hall.name} | {order.seat.name} and payment is Pending',
                msg_typ='confirmation',
                amount=payment.order.order_amount(),
                payment_method=payment.payment_method,
                payment_status=payment.status,
                max_time=order.max_time()
                )            

        return redirect('theatre:waiting-for-cash-order', order.pk)
    
    except Exception as e:
        return HttpResponse(str(e))
        
        raise Http404('page not found')
    

def waiting_for_cash_order(request, pk):
    try:
        order = Order.objects.get(pk=pk)

        order = get_object_or_404(Order, pk=pk)

        meta_data = {
            'theatre_id': order.seat.row.hall.theatre.pk,
            'app': 'Theatre Application',
            'theatre_name': order.seat.row.hall.theatre.name,
        }

        payment = order.payment

        if payment.status != "Created":
            # Payment is completed
            return redirect('theatre:order-status', order.pk)

        if payment.gateway == 'split_razorpay':
            gateway_detail = PaymentGateway.objects.get(name='split_razorpay')

            context = {
                'order': order,  # Pass the seat information to the template
                'theatre_id': meta_data["theatre_id"],
                "theatre_name": meta_data['theatre_name'],
            }
            return render(request, 'theatre/Razorpay/waiting-for-cash.html', context)

        # if payment gateway is razorpay
        elif payment.gateway == 'Razorpay':
            gateway_detail = PaymentGateway.objects.get(name='Razorpay')
            order_id = payment.razorpaypayment.razorpay_order_id

            # convert amount into INR
            amount = payment.amount * 100 

            amount = round(amount, 2)

            # Send order details to the template
            context = {
                'order_id': order_id,
                'amount': amount,
                'visible_amount': amount / 100,
                'razorpay_key': gateway_detail.gateway_key,  # Razorpay publishable key
                'order': order,  # Pass the seat information to the template
                'app': meta_data["app"],
                'theatre_id': meta_data["theatre_id"],
                "theatre_name": meta_data['theatre_name'],
            }
            

            return render(request, 'theatre/Razorpay/waiting-for-cash.html', context)
        
        elif payment.gateway == 'Cashfree':
            gateway_detail = PaymentGateway.objects.get(name='Cashfree')
            cashfree_detail = payment.cashfreepayment
            order_id = cashfree_detail.cashfree_order_id
            amount = payment.amount

            context = {
                'order_id': order.pk,
                'amount': amount,
                'order': order,
                'cashfree_detail': cashfree_detail,
                'redirect_url': request.build_absolute_uri(reverse('theatre:cashfree-payment-callback', args=[order.pk])),
            }

            # convert amount into INR
            return render(request, 'theatre/Cashfree/waiting-for-cash.html', context)

    except:
        raise Http404('page not found')
    

@login_required
def get_seat_last_order(request, pk):
    if user_has_permission(request.user, "view_order"):
        try:
            seat = Seat.objects.get(pk=pk)
            last_order = seat.order_set.last()
            return redirect('theatre:initiate-payment', pk=last_order.pk)
        except:
            raise Http404('page not found')
        
    else:
        return HttpResponse('Permission Denied')
    
@login_required
def cancel_cash_order(request, pk):
    if user_has_permission(request.user, "view_order"):
        try:
            order = Order.objects.get(pk=pk)   
            seat = order.seat
            seat.is_vacent = True
            seat.save()

            # UPDATE THE SEAT STATUS VIA WEBSOCKET
            update_websocket(
                theatre_id=order.seat.row.hall.theatre.id,
                seat_id=order.seat.id,
                is_vacent=order.seat.is_vacent,
                order_id=order.id,
                payment_panding=True,
                seat_name=f"{order.seat.row.hall.name} | {order.seat.name}",
                bg_type="bg-danger",
                message=f'Order From Seat {order.seat.row.hall.name} | {order.seat.name} is Canceled !',
                msg_typ='Cancelation'
                )
            
            # DELETE THE ORDER
            order.delete()
            return HttpResponse('Order from Seat is Canceled')
        except:
            raise Http404('page not found')
        
    else:
        return HttpResponse('Permission Denied')

@login_required
def add_cash_payment(request, pk):
    if user_has_permission(request.user, "view_order"):
        try:
            order = Order.objects.get(pk=pk)
            if request.user.userprofile.theatre == order.seat.row.hall.theatre:
                seat = order.seat
                seat.is_vacent = False
                seat.save()
                theatre = seat.row.hall.theatre

                # just for simple purpose
                payment = order.payment
                payment.payment_method = 'Cash'
                payment.status = 'Success'
                payment.time=localtime(timezone.now())
                payment.save()

                order_profile_url = reverse("theatre:order-profile", args=[order.pk])
                order_profile_url = f"https://www.scan2food.com{order_profile_url}"
                
                update_websocket(
                    theatre_id=order.seat.row.hall.theatre.id,
                    theatre_name=order.seat.row.hall.theatre.name,
                    order_id=order.id,
                    seat_id=order.seat.id,
                    is_vacent=order.seat.is_vacent,
                    payment_panding=True,
                    seat_name=f"{seat.row.hall.name} | {seat.name}",
                    bg_type='bg-warning',
                    message=f'New Order Come From {order.seat.row.hall.name} | {order.seat.name} and payment is Pending',
                    msg_typ='confirmation',
                    amount=payment.order.order_amount(),
                    payment_method=payment.payment_method,
                    payment_status=payment.status,
                    max_time=order.max_time()
                    )
                # order generated Refulect to the Dashboard

                return redirect("theatre:order-status", pk=order.id)

            else:
                return HttpResponse('Permission Denied')

        except:
            raise Http404('page not found')
        
    else:
        return HttpResponse('Permission Denied')

@login_required
def print_bill(request, pk):
    if user_has_permission(request.user, "view_order"):
        try:
            order = Order.objects.get(pk=pk)
            if request.user.userprofile.theatre == order.seat.row.hall.theatre:
                convinient_amount = order.payment.amount - order.full_payment()
                convinient_charges = order.seat.row.hall.theatre.detail.commission()
                convinient_amount = round(convinient_amount, 2)
                convinient_fee = {"perscentage": convinient_charges, "amount": convinient_amount}
                return render(request, 'theatre/bill.html', {'order': order, "convinient_fee": convinient_fee})
            else:
                return HttpResponse('Permission Denied')
        except:
            raise Http404('page not found')
        
    else:
        return HttpResponse('Permission Denied')

@login_required
def print_kot(request, pk):
    if user_has_permission(request.user, "view_order"):
        try:
            order = Order.objects.get(pk=pk)
            if request.user.userprofile.theatre == order.seat.row.hall.theatre:
                return render(request, 'theatre/kot.html', {'order': order})
            else:
                return HttpResponse('Permission Denied')
        except:
            raise Http404('page not found')
        
    else:
        return HttpResponse('Permission Denied')

@login_required
def all_users(request):
    if user_has_permission(request.user, "add_userprofile"):
        user_type = request.GET.get('user-type', 'all')
        login_id = request.GET.get('login-id', '')
        user_name = request.GET.get('user-name', '')
        active_status = request.GET.get('active-status', 'all')
        theatre = request.user.userprofile.theatre

        all_users = UserProfile.objects.filter(theatre=theatre, user__username__icontains=login_id, user__first_name__icontains=user_name)

        if user_type != "all":
            user_group = Group.objects.filter(name=user_type).first()
            all_users = all_users.filter(user__groups=user_group)

        if active_status != 'all':
            if active_status == 'true':
                active_status = True
            else:
                active_status = False
            all_users = all_users.filter(active_status=active_status)

            if active_status:
                active_status = 'true'
            else:
                active_status = 'false'

        paginator = Paginator(all_users, 10)  # Show 10 items per page.

        page_number = request.GET.get('page')
        if page_number == None:
            page_number = 1
        all_users = paginator.get_page(page_number)

        form = SimpleUserProfileForm()
        
        return render(request, 'theatre/all-users.html', {"all_users": all_users, "form": form, 'user_type': user_type, "login_id": login_id, 'user_name': user_name, 'active_status': active_status})

    else:
        return HttpResponse('Permission Denied')

@login_required
def create_simple_user(request):
    if user_has_permission(request.user, "add_userprofile"):
        if request.method == 'POST':
            form = SimpleUserProfileForm(request.POST)
            if form.is_valid():
                theatre = request.user.userprofile.theatre
                name = form.cleaned_data['name']
                phone_number = form.cleaned_data['phone_number']
                password = form.cleaned_data['password']
                user_type = form.cleaned_data['user_type']
                if user_type == 'admin' or user_type == 'service_provider':
                    messages.error(request, f"You Haven't Access to create an Admin User")
                    return redirect('theatre:all-users')
                try:

                    # CREATE A NEW USER
                    user = User.objects.create(
                        username=phone_number,
                        password=make_password(password),
                        first_name = name
                    )

                    # GET THE GROUP
                    group = Group.objects.filter(name=user_type).first()

                    # CREATING THE USER PROFILE PAGE
                    UserProfile.objects.create(user=user, theatre=theatre)

                    # ADDING THE USER TO THE GROUP
                    user.groups.add(group)

                    # return a success message
                    messages.success(request, 'New User is Added in Your Theatre')
                except IntegrityError as e:
                    messages.error(request, f'UserId {phone_number} is Alrady There So create user with another User Id')

            return redirect('theatre:all-users')
        
        else:
            return HttpResponse('Method Not Allowed')
    else:
        return HttpResponse('Permission Denied')


def show_menu(request, pk):
    try:
        seat = Seat.objects.get(pk=pk)
        theatre = seat.row.hall.theatre
        
        service_end_time = theatre.service_end_time
        service_start_time = dt.time(6, 0)

        current_time = localtime(timezone.now()).time()
        is_activate = False

        if service_end_time.hour < 6:
            # after 12:00 AM
            if current_time.hour > 6:
                is_activate = True
            
            else:
                if current_time <= service_end_time:
                    is_activate = True

            
        else:
            # before 12:00 AM
            if service_start_time <= current_time <= service_end_time:
                is_activate = True
            else:
                is_activate = False
        
        if theatre.detail.scaning_service == False:
            return render(request, 'website/service-out.html')
        
        elif theatre.detail.is_active == False:
            # check the break time and if the break time is less then automatic activate the service
            return render(request, 'website/service-out.html')

        if seat.is_vacent == True:
            # check current time
            if is_activate == False:
                return render(request, 'website/service-out.html')

            try:
                discount = theatre.discount
            except:
                discount = None

            pending_orders = Order.objects.filter(seat__row__hall__theatre=theatre, payment__status='Success', delivery_time=None).count()
            if pending_orders >= theatre.order_limit:
                return render(request, 'theatre/over-order.html')

            return render(request, 'theatre/show-new-menu.html', {
                'seat': seat, 
                'theatre': theatre, 
                'discount': discount,
                'api_key': settings.API_KEY  # Pass API key to template
            })
                
        else:
            last_order = Order.objects.filter(seat=seat, seat__is_vacent=False).last()
            if last_order.payment.status == 'Created':
                return redirect('theatre:initiate-payment', last_order.pk)
            
            else:
                delivery_time = last_order.delivery_time
            
                if delivery_time != None:
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
                        order_id=last_order.pk,
            )

                    return redirect('theatre:show-menu', pk=seat.pk)
                
                return redirect('theatre:order-status', last_order.pk)
    
    except:
        raise Http404('page not found')

def single_qr(request, pk):
    try:
        context = {
            'theatre_id': pk
        }
        return render(request, 'theatre/single-qr.html', context)
    
    except:
        raise Http404('page not found')

def hall_qr(request, pk):
    try:
        hall = Hall.objects.get(pk=pk)
        context = {
            'theatre_id': hall.theatre.pk,
            'hall': hall
        }
        return render(request, 'theatre/hall-template.html', context)

    except Exception as e:
        print('error ==>', e, '\n\n')

        raise Http404('page not found')
    

def order_status(request, pk):
    try:
        order = Order.objects.get(pk=pk)
        
        if request.method == "POST":
            data = request.body
            data = json.loads(data)
            phone_number = data['phone_number']
            notes = data['notes']
            order.notes = notes
            payment = order.payment
            payment.phone_number = phone_number
            # SAVE THE NOTES AND PHONE NUMBER IN PAYMENT AND ORDER
            order.save()
            payment.save()
            return JsonResponse({'status': True})
        else:

            try:
                refund_request = order.orderrefundrequest
                if not refund_request.resolve_status:
                    return HttpResponse('<h3>Our Team will connect you After Your Movie is Over</h3>')
                
                else:
                    return HttpResponse('<h3>Your Refund is Canceled...</h3>')
            except:
                pass

            if order.seat.row.hall.theatre.detail.payment_model == 'theatre':
                return render(request, 'theatre/order-status.html', {'order': order})
            

            elif order.delivery_time != None:
                return redirect('theatre:order-feedback', order.pk)
            
            else:
                order_time = localtime(order.payment.time)
                order_time = order_time.strftime("%d-%b-%Y %I:%M %p")
                max_time = order.max_time()
                return render(request, 'theatre/order-preparing.html', {'order': order, "order_time": order_time, "max_time": max_time})
    
    except:
        raise Http404('page not found')
    
def order_feedback(request, pk):
    order = Order.objects.get(pk=pk)
    
    if request.method == 'POST':
        data = request.body
        data = json.loads(data)
        ratting = data['ratting']
        comment = data['comment']
        
        order.rating = ratting
        order.comment = comment
        order.review_done = True
        order.save()

        return JsonResponse({'status': 'done'})

    if order.delivery_time != None:
        if order.review_done:
            return render(request, 'theatre/review-completed.html', {'order': order})

        return render(request, 'theatre/order-feedback.html', {'order': order})
    else:        
        return redirect('theatre:order-status', order.pk)
        
def initiate_payment(request, pk):
    try:
        order = get_object_or_404(Order, pk=pk)
        
        # Customer isn't able to do the payment after the time completion

        theatre = order.seat.row.hall.theatre
        service_end_time = theatre.service_end_time
        service_start_time = dt.time(6, 0)

        current_time = localtime(timezone.now()).time()
        is_activate = False

        if service_end_time.hour < 6:
            # after 12:00 AM
            if current_time.hour > 6:
                is_activate = True
            
            else:
                if current_time <= service_end_time:
                    is_activate = True

            
        else:
            # before 12:00 AM
            if service_start_time <= current_time <= service_end_time:
                is_activate = True
            else:
                is_activate = False
        
        if theatre.detail.scaning_service == False:
            return render(request, 'website/service-out.html')
        
        elif theatre.detail.is_active == False:
            # check the break time and if the break time is less then automatic activate the service
            return render(request, 'website/service-out.html')

        elif is_activate == False:
            return render(request, 'website/service-out.html')

        # After the time is valid to cheeck the timing with theatre time


        meta_data = {
            'theatre_id': order.seat.row.hall.theatre.pk,
            'app': 'Theatre Application',
            'theatre_name': order.seat.row.hall.theatre.name,
        }

        payment = order.payment

        if payment.status != "Created":
            # Payment is completed
            return redirect('theatre:order-status', order.pk)

        elif payment.gateway == "split_razorpay":
            gateway_detail = PaymentGateway.objects.get(name='split_razorpay')
            order_id = payment.splitrazorpaypayment.razorpay_order_id

            # convert amount into INR
            amount = payment.amount * 100 

            amount = round(amount, 2)

            # Send order details to the template
            context = {
                'order_id': order_id,
                'amount': amount,
                'visible_amount': amount / 100,
                'razorpay_key': gateway_detail.gateway_key,  # Razorpay publishable key
                'order': order,  # Pass the seat information to the template
                'app': meta_data["app"],
                'theatre_id': meta_data["theatre_id"],
                "theatre_name": meta_data['theatre_name'],
            }
            
            return render(request, 'theatre/SplitRazorpay/payment-page.html', context)

        
        elif payment.gateway == 'Razorpay':
            gateway_detail = PaymentGateway.objects.get(name='Razorpay')
            order_id = payment.razorpaypayment.razorpay_order_id

            # convert amount into INR
            amount = payment.amount * 100 

            amount = round(amount, 2)

            # Send order details to the template
            context = {
                'order_id': order_id,
                'amount': amount,
                'visible_amount': amount / 100,
                'razorpay_key': gateway_detail.gateway_key,  # Razorpay publishable key
                'order': order,  # Pass the seat information to the template
                'app': meta_data["app"],
                'theatre_id': meta_data["theatre_id"],
                "theatre_name": meta_data['theatre_name'],
            }
            
            return render(request, 'theatre/Razorpay/payment-page.html', context)
        
        elif payment.gateway == 'Cashfree':

            amount = payment.amount
            cashfree_detail = payment.cashfreepayment
            context = {
                'order_id': order.pk,
                'amount': amount,
                'order': order,
                'cashfree_detail': cashfree_detail,
                'redirect_url': request.build_absolute_uri(reverse('theatre:cashfree-payment-callback', args=[order.pk])),
            }
            return render(request, 'theatre/Cashfree/payment-page.html', context)
        
        elif payment.gateway == 'Phonepe':
            # get phonepe details
            selected_gateway = PaymentGateway.objects.filter(name="Phonepe").first()
            client_id = selected_gateway.gateway_key
            client_secret = selected_gateway.gateway_secret
            client_version = 1  
            env=Env.PRODUCTION
            client = StandardCheckoutClient.get_instance(client_id=client_id,
                                                                client_secret=client_secret,
                                                                client_version=client_version,
                                                                env=env)

            # check about the payment status

            unique_order_id = payment.phonepepayment.uu_id
            order_response = client.get_order_status(merchant_order_id=unique_order_id)
            order_status = order_response.state

            if order_status == "PENDING":
                pass

            elif order_status == 'COMPLETED':
                # update the payment
                return redirect('theatre:phonepe-payment-callback', order.pk)
            else:
                # delete the phonepe object and create new object for same order 
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
                phone_pe_obj = payment.phonepepayment
                phone_pe_obj.payment = payment
                phone_pe_obj.uu_id = unique_order_id
                phone_pe_obj.order_id = order_id
                phone_pe_obj.payment_url = payment_url
                phone_pe_obj.save()

            amount = payment.amount
            context = {
                'amount': amount,
                'order': order,
            }
            return render(request, 'theatre/Phonepe/payment-page.html', context)
        
        elif payment.gateway == 'CCAvenue':
            amount = payment.amount
            gateway_detail = PaymentGateway.objects.get(name='CCAvenue')
            context = {
                'order_id': order.pk,
                'amount': amount,
                'order': order,
                'redirect_url': request.build_absolute_uri(reverse('theatre:ccavenue-payment-request-handler', args=[order.pk])),
            }
            return render(request, 'theatre/CCAvenue/payment-page.html', context)

        elif payment.gateway == 'PayU':
            try:
                gateway_detail = PaymentGateway.objects.get(name='PayU')
                uu_id = payment.payupayment.uu_id
                hash_string = f"{gateway_detail.gateway_key}|verify_payment|{uu_id}|{gateway_detail.gateway_salt}"

                hashh = hashlib.sha512(hash_string.encode('utf-8')).hexdigest()

                url = "https://info.payu.in/merchant/postservice.php?form=2"
                # url = "https://test.payu.in/merchant/postservice?form=2"

                payload = {
                    "key": gateway_detail.gateway_key,
                    "command": "verify_payment",
                    "var1": uu_id,
                    "hash": hashh
                }
                
                response = requests.post(url, data=payload)
                response_data = response.json()
                
                if response_data['transaction_details'][uu_id]['status'] == 'success':
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

                    # update the websocket
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
                        group=seat.row.hall.theatre.group,
                        theatre_name=seat.row.hall.theatre.name,
                        msg_typ="confirmation",
                        payment_method=payment.payment_method,
                        payment_status=payment.status,
                        amount=payment.order.order_amount(),
                        order_id=payment.order.pk,
                        max_time=payment.order.max_time()
                        )
                    
                    return redirect('theatre:order-status', order.pk)
            except:
                pass
            amount = payment.amount
            context = {
                'amount': amount,
                'order': order,
            }
            return render(request, 'theatre/Payu/payment-page.html', context)
        
        else:
            # Unknown payment gateway
            return HttpResponse('Payment gateway not configured properly', status=400)

    except Exception as e:
        return HttpResponse(f'error {e}')
        raise Http404('page not found')

@never_cache
def ccavenueRequestHandler(request, pk):
    try:
        order = Order.objects.get(pk=pk)
        payment = order.payment
        if payment.gateway == 'CCAvenue':
            # Payment is completed
            gateway = PaymentGateway.objects.get(name='CCAvenue')
            merchant_id = gateway.merchant_id
            access_code = gateway.access_code
            working_key = gateway.working_key

            theatre = order.seat.row.hall.theatre
            theatre_mail = theatre.name
            theatre_mail = theatre_mail.replace(" ", ".")

            try:
                uu_id = payment.ccavenuepayment.uu_id

                # CHECK WHETHER THE PAYMENT IS ALREADY DONE OR NOT

            except:
                uu_id = str(uuid4())
                
                while True:
                    sameuuid = CCAvenuePayment.objects.filter(uu_id=uu_id).first()
                    if sameuuid == None:
                        break
                    else:
                        continue

                # create a new instance of the CCAvenue PAYMENT
                CCAvenuePayment.objects.create(
                    payment=payment,
                    uu_id=uu_id,
                    traking_id=f"temp_{uu_id}",
                    bank_ref_no=f"temp_{uu_id}",
                    )
                
            p_merchant_id = str(merchant_id) # required
            p_order_id = str(uu_id) # required
            p_currency = 'INR' # required
            p_amount = str(payment.amount) # required

            redirect_url = request.build_absolute_uri(reverse('theatre:ccavenue-payment-callback', args=[order.pk]))
            p_redirect_url = redirect_url.replace("http://", "https://") # required
            p_cancel_url = redirect_url.replace("http://", "https://") # required
            
            
            p_language = 'EN' # required
            p_billing_name = theatre.owner_name # required
            p_billing_address = theatre.address # required
            p_billing_city = theatre.detail.city # required
            p_billing_state = theatre.detail.state # required
            p_billing_zip = theatre.detail.zip # required
            p_billing_country = 'India' # required
            p_billing_tel = payment.phone_number # required
            p_billing_email = f"{theatre_mail}@scan2food.com"
            
            p_integration_type = 'iframe_normal'

            
            # REDIRECT TO THE CCAVANUE PAYMENT PAGE
            merchant_data='merchant_id='+ p_merchant_id+'&'+'order_id='+p_order_id + '&' + "currency=" + p_currency + '&' + 'amount=' + p_amount+'&'+'redirect_url='+p_redirect_url+'&'+'cancel_url='+p_cancel_url+'&'+'language='+p_language+'&'+'billing_name='+p_billing_name+'&'+'billing_address='+p_billing_address+'&'+'billing_city='+p_billing_city+'&'+'billing_state='+p_billing_state+'&'+'billing_zip='+p_billing_zip+'&'+'billing_country='+p_billing_country+'&'+'billing_tel='+p_billing_tel+'&'+'billing_email='+p_billing_email+'&'+'integration_type='+p_integration_type
            encryption = encrypt(merchant_data, working_key)

            context = {
                'mid': p_merchant_id,
                'encReq': encryption,
                'xscode': access_code
            }

            return render(request, 'theatre/CCAvenue/payment-frame.html', context)
        
        else:
            raise Http404('page not found')
         
    except:
        raise Http404('page not found')

@never_cache
def initiate_test_payment(request, pk):
    try:
        request.session.modified = True  # Mark session as modified
        request.session.cycle_key()  # Generates a new session ID
        
        order = get_object_or_404(Order, pk=pk)

        meta_data = {
            'theatre_id': order.seat.row.hall.theatre.pk,
            'app': 'Theatre Application',
            'theatre_name': order.seat.row.hall.theatre.name,
        }

        payment = order.payment

        if payment.status != "Created":
            # Payment is completed
            return redirect('theatre:order-status', order.pk)

        if payment.gateway == 'Razorpay':
            gateway_detail = PaymentGateway.objects.get(name='Razorpay')
            order_id = payment.razorpaypayment.razorpay_order_id

            # convert amount into INR
            amount = payment.amount * 100 

            amount = round(amount, 2)

            # Send order details to the template
            context = {
                'order_id': order_id,
                'amount': amount,
                'visible_amount': amount / 100,
                'razorpay_key': gateway_detail.gateway_key,  # Razorpay publishable key
                'order': order,  # Pass the seat information to the template
                'app': meta_data["app"],
                'theatre_id': meta_data["theatre_id"],
                "theatre_name": meta_data['theatre_name'],
            }
            
            return render(request, 'theatre/Razorpay/payment-page.html', context)
        
        elif payment.gateway == 'Cashfree':
            amount = payment.amount * 100 


            amount = payment.amount
            cashfree_detail = payment.cashfreepayment
            context = {
                'order_id': order.pk,
                'amount': amount,
                'order': order,
                'cashfree_detail': cashfree_detail,
                'redirect_url': request.build_absolute_uri(reverse('theatre:cashfree-payment-callback', args=[order.pk])),
            }
            return render(request, 'theatre/Cashfree/test-page.html', context)

    except:
        raise Http404('page not found')
    
def split_razorpay_payment_callback(request):
    if request.method == "POST":

        # Get payment details from Razorpay callback

        payment_id = request.POST.get('razorpay_payment_id', '')
        order_id = request.POST.get('razorpay_order_id', '')
        signature = request.POST.get('razorpay_signature', '')

        # ⚠️ SECURITY: Payment confirmation moved to webhook for security
        # This callback only saves payment IDs and redirects to order status
        # Actual payment confirmation happens in api_views.py webhook after signature verification
        
        try:
            # Save payment IDs for reference
            razorpay_payment = SplitRazorpayPayment.objects.get(razorpay_order_id=order_id)
            payment = razorpay_payment.payment
            
            razorpay_payment.razorpay_payment_id = payment_id
            razorpay_payment.razorpay_signature = signature
            razorpay_payment.save()
            
            # COMMENTED OUT: Payment confirmation now happens ONLY in webhook
            # This prevents bypassing webhook security verification
            # The webhook in api_views.py will:
            # 1. Verify signature using gateway_salt
            # 2. Confirm payment status
            # 3. Update seat and send notifications
            
            # if payment.status != 'Success':
            #     payment.payment_method = 'Gateway'
            #     payment.phone_number = payment_data['contact']
            #     payment.status = "Success"
            #     payment.time=localtime(timezone.now())
            #     payment.save()
            #     seat = payment.order.seat
            #     seat.is_vacent = False
            #     seat.save()
            #     ... (websocket update code)

            # Redirect to order status page (webhook will confirm payment)
            return redirect('theatre:order-status', payment.order.pk)

        except Exception as e:
            # Log error but don't fail - webhook will handle confirmation
            print(f"❌ Callback error: {str(e)}")
            return HttpResponse("Processing payment...")

    return HttpResponse("Invalid request")

def razorpay_payment_callback(request):
    if request.method == "POST":

        # Get payment details from Razorpay callback

        payment_id = request.POST.get('razorpay_payment_id', '')
        order_id = request.POST.get('razorpay_order_id', '')
        signature = request.POST.get('razorpay_signature', '')

        # ⚠️ SECURITY: Payment confirmation moved to webhook for security
        # This callback only saves payment IDs and redirects to order status
        # Actual payment confirmation happens in api_views.py webhook after signature verification
        
        try:
            # Save payment IDs for reference
            razorpay_payment = RazorpayPayment.objects.get(razorpay_order_id=order_id)
            payment = razorpay_payment.payment
            
            razorpay_payment.razorpay_payment_id = payment_id
            razorpay_payment.razorpay_signature = signature
            razorpay_payment.save()
            
            # COMMENTED OUT: Payment confirmation now happens ONLY in webhook
            # This prevents bypassing webhook security verification
            # The webhook in api_views.py will:
            # 1. Verify signature using gateway_salt
            # 2. Confirm payment status
            # 3. Update seat and send notifications
            
            # if payment.status != 'Success':
            #     payment.payment_method = 'Gateway'
            #     payment.phone_number = payment_data['contact']
            #     payment.status = "Success"
            #     payment.time=localtime(timezone.now())
            #     payment.save()
            #     seat = payment.order.seat
            #     seat.is_vacent = False
            #     seat.save()
            #     ... (websocket update code)

            # Redirect to order status page (webhook will confirm payment)
            return redirect('theatre:order-status', payment.order.pk)

        except Exception as e:
            # Log error but don't fail - webhook will handle confirmation
            print(f"❌ Callback error: {str(e)}")
            return HttpResponse("Processing payment...")

    return HttpResponse("Invalid request")

@csrf_exempt
def cashfree_payment_callback(request, pk):
    try:
        order = Order.objects.get(pk=pk)
        payment = order.payment
        if payment.status == 'Refunded':
            raise Http404('page not found')
        
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

                order_profile_url = reverse("theatre:order-profile", args=[order.pk])
                order_profile_url = f"https://www.scan2food.com{order_profile_url}"

                # update the websocket
                update_websocket(
                    theatre_id=seat.row.hall.theatre.id,
                    seat_id=seat.id,
                    is_vacent=seat.is_vacent,
                    payment_panding=False,
                    seat_name=f"{seat.row.hall.name} | {seat.name}",
                    message= f'New Order Come From Seat {seat.row.hall.name} | {seat.name}  %0A%0A Order Profile:- {order_profile_url}',
                    customer_phone=order.payment.phone_number,
                    customer_message=cusotmer_message,
                    notification_numbers=seat.row.hall.theatre.notification_numbers,
                    group=seat.row.hall.theatre.group,
                    theatre_name=seat.row.hall.theatre.name,
                    msg_typ="confirmation",
                    payment_method=payment.payment_method,
                    payment_status=payment.status,
                    amount=payment.order.order_amount(),
                    order_id=payment.order.pk,
                    max_time=payment.order.max_time()
                )

                # Perform any task on success, e.g., marking the seat's order as paid
                return redirect('theatre:order-status', payment.order.pk)
        
            else:
                # Show the initiate payment again
                return redirect('theatre:initiate-payment', pk=order.pk)

        else:
            # Perform any task on success, e.g., marking the seat's order as paid
            return redirect('theatre:order-status', payment.order.pk)
    except:
        raise Http404('page not found')

@csrf_exempt
def phonepe_payment_callback(request, pk):
    try:
        order = Order.objects.get(pk=pk)
        payment = order.payment
        if payment.status == 'Refunded':
            raise Http404('page not found')

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

                # send to websocket
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
                    group=seat.row.hall.theatre.group,
                    theatre_name=seat.row.hall.theatre.name,
                    msg_typ="confirmation",
                    payment_method=payment.payment_method,
                    payment_status=payment.status,
                    amount=payment.order.order_amount(),
                    order_id=payment.order.pk,
                    max_time=payment.order.max_time()
                )
                # Perform any task on success, e.g., marking the seat's order as paid
                return redirect('theatre:order-status', payment.order.pk)

            else:
                # return again to initiate payment
                return redirect('theatre:initiate-payment', pk=order.pk)

        else:
            # Perform any task on success, e.g., marking the seat's order as paid
            return redirect('theatre:order-status', payment.order.pk)
    except:
        pass

@csrf_exempt
def ccavenue_payment_callback(request, pk):
    try:
        order = Order.objects.get(pk=pk)
        payment = order.payment
        if payment.status == 'Refunded':
            raise Http404('page not found')

        if payment.status != 'Success':
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
                # Make the payment success
                if payment.ccavenuepayment.uu_id == payment_data['order_id']:
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
                        group=seat.row.hall.theatre.group,
                        theatre_name=seat.row.hall.theatre.name,
                        msg_typ="confirmation",
                        payment_method=payment.payment_method,
                        payment_status=payment.status,
                        amount=order.order_amount(),
                        order_id=order.pk,
                        max_time=payment.order.max_time()
                    )

                else:
                    return HttpResponse('Payment ID does not match with the order ID')

                return redirect('theatre:order-status', payment.order.pk)

            else:
                return JsonResponse(payment_data)
            
        else:
            return redirect('theatre:order-status', payment.order.pk)
        
    except:
        raise Http404('page not found')
    

@csrf_exempt
def payu_payment_callback(request, pk):
    try:
        order = Order.objects.get(pk=pk)
        payment = order.payment

        gateway_detail = PaymentGateway.objects.get(name='PayU')

        if payment.status == 'Refunded':
            raise Http404('page not found')

        if payment.status != 'Success':
            # get the transaction details
            transaction_id = request.POST.get('txnid')
            if transaction_id == payment.payupayment.uu_id:
                # right payment ! perform to add the payment
                # get the status
                status = request.POST.get('status')

                if status == 'success':
                    order_id = request.POST.get('mihpayid')

                    # check from the payu gateway
                    payment.payupayment.order_id = order_id
                    hash_string = f"{gateway_detail.gateway_key}|verify_payment|{order_id}|{gateway_detail.gateway_salt}"

                    hashh = hashlib.sha512(hash_string.encode('utf-8')).hexdigest()

                    url = "https://info.payu.in/merchant/postservice.php?form=2"
                    # # url = "https://test.payu.in/merchant/postservice?form=2"

                    payload = {
                        "key": gateway_detail.gateway_key,
                        "command": "verify_payment",
                        "var1": order_id,
                        "hash": hashh
                    }
                    
                    response = requests.post(url, data=payload)
                    response_data = response.json()
                    
                    if response_data['transaction_details'][order_id]['status'] == 'success':
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
                            group=seat.row.hall.theatre.group,
                            theatre_name=seat.row.hall.theatre.name,
                            msg_typ="confirmation",
                            payment_method=payment.payment_method,
                            payment_status=payment.status,
                            amount=order.order_amount(),
                            order_id=order.pk,
                            max_time=payment.order.max_time()
                        )

                        return redirect('theatre:order-status', payment.order.pk)



            return redirect('theatre:initiate-payment', pk=order.pk)
    


        else:
            return redirect('theatre:order-status', payment.order.pk)
        
    except Exception as e:
        raise Http404('page not found')

@login_required
def seat_qr(request):
    if user_has_permission(request.user, "view_seat"):
        request_ids = request.GET.get('ids')
        request_halls = request.GET.get('halls')

        if request_ids != None:
            all_ids = request_ids.split(",")
            seats = []
            for id in all_ids:
                seat = Seat.objects.get(pk=id)
                seats.append(seat)
            
            return render(request, 'theatre/old-qr-code.html', {'seats': seats})
             
        elif request_halls != None:
            all_halls = request_halls.split(",")
            seats = []
            for hall_name in all_halls:
                hall = Hall.objects.filter(name=hall_name, theatre=request.user.userprofile.theatre).first()
                hall_seats = Seat.objects.filter(row__hall=hall)
                for seat in hall_seats:
                    seats.append(seat)

            return render(request, 'theatre/old-qr-code.html', {'seats': seats})
        
        theatre = request.user.userprofile.theatre
        seats = Seat.objects.filter(row__hall__theatre=theatre)
        paginator = Paginator(seats, 200)  # Show 12 items per page.

        page_number = request.GET.get('page')
        if page_number == None:
            page_number = 1
        seats = paginator.get_page(page_number)

        return render(request, 'theatre/old-qr-code.html', {'seats': seats})
    else:
        return HttpResponse('Permission Denied')

@login_required
def new_seat_qr(request):
    if user_has_permission(request.user, "view_seat"):
        theatre = request.user.userprofile.theatre
        request_ids = request.GET.get('ids')
        request_halls = request.GET.get('halls')

        if request_ids != None:
            all_ids = request_ids.split(",")
            seats = []
            for id in all_ids:
                seat = Seat.objects.get(pk=id)
                seats.append(seat)
            
            return render(request, 'theatre/new-qr-code.html', {'seats': seats, 'theatre': theatre})
             
        elif request_halls != None:
            all_halls = request_halls.split(",")
            seats = []
            for hall_name in all_halls:
                hall = Hall.objects.filter(name=hall_name, theatre=request.user.userprofile.theatre).first()
                hall_seats = Seat.objects.filter(row__hall=hall)
                for seat in hall_seats:
                    seats.append(seat)

            return render(request, 'theatre/new-qr-code.html', {'seats': seats, 'theatre': theatre})

        seats = Seat.objects.filter(row__hall__theatre=theatre)
        paginator = Paginator(seats, 200)  # Show 12 items per page.

        page_number = request.GET.get('page')
        if page_number == None:
            page_number = 1
        seats = paginator.get_page(page_number)

        return render(request, 'theatre/new-qr-code.html', {'seats': seats, 'theatre': theatre})
    else:
        return HttpResponse('Permission Denied')

@login_required
def acrylic_small_qr(request):
    if user_has_permission(request.user, "view_seat"):
        request_ids = request.GET.get('ids')
        request_halls = request.GET.get('halls')

        if request_ids != None:
            all_ids = request_ids.split(",")
            seats = []
            for id in all_ids:
                seat = Seat.objects.get(pk=id)
                seats.append(seat)
            
            return render(request, 'theatre/acrylic-small-qr.html', {'seats': seats})
             
        elif request_halls != None:
            all_halls = request_halls.split(",")
            seats = []
            for hall_name in all_halls:
                hall = Hall.objects.filter(name=hall_name, theatre=request.user.userprofile.theatre).first()
                hall_seats = Seat.objects.filter(row__hall=hall)
                for seat in hall_seats:
                    seats.append(seat)

            return render(request, 'theatre/acrylic-small-qr.html', {'seats': seats})
        
        theatre = request.user.userprofile.theatre
        seats = Seat.objects.filter(row__hall__theatre=theatre)
        paginator = Paginator(seats, 200)  # Show 12 items per page.

        page_number = request.GET.get('page')
        if page_number == None:
            page_number = 1
        seats = paginator.get_page(page_number)

        return render(request, 'theatre/acrylic-small-qr.html', {'seats': seats})
    else:
        return HttpResponse('Permission Denied')


@login_required
def new_qr(request):
    if user_has_permission(request.user, "view_seat"):
        request_ids = request.GET.get('ids')
        request_halls = request.GET.get('halls')

        if request_ids != None:
            all_ids = request_ids.split(",")
            seats = []
            for id in all_ids:
                seat = Seat.objects.get(pk=id)
                seats.append(seat)
            
            return render(request, 'theatre/new-qr.html', {'seats': seats})
             
        elif request_halls != None:
            all_halls = request_halls.split(",")
            seats = []
            for hall_name in all_halls:
                hall = Hall.objects.filter(name=hall_name, theatre=request.user.userprofile.theatre).first()
                hall_seats = Seat.objects.filter(row__hall=hall)
                for seat in hall_seats:
                    seats.append(seat)

            return render(request, 'theatre/new-qr.html', {'seats': seats})
        
        theatre = request.user.userprofile.theatre
        seats = Seat.objects.filter(row__hall__theatre=theatre)
        paginator = Paginator(seats, 200)  # Show 12 items per page.

        page_number = request.GET.get('page')
        if page_number == None:
            page_number = 1
        seats = paginator.get_page(page_number)

        return render(request, 'theatre/new-qr.html', {'seats': seats})
    else:
        return HttpResponse('Permission Denied')

@login_required
def refund_order(request, pk):
    if request.method == 'POST':
        try:
            otp = request.POST.get('otp')
            reason = request.POST.get('reason')
            order = Order.objects.get(pk=pk)
            payment = order.payment

            if order.refund_otp == otp:
                
                if payment.payout == None:
                    if payment.payment_method == 'Gateway':
                        
                        if payment.status == 'Refunded':
                            messages.error(request, 'Payment has already been settled and cannot be refunded.')

                        else:
                            refund_generated = False
                            if payment.gateway == "split_razorpay":
                                # CODE IS WORKING AND COMPLETED FOR SPLIT RAZORPAY
                                pay_id = payment.splitrazorpaypayment.razorpay_payment_id
                                amount = payment.amount * 100
                                refund_url = f'https://api.razorpay.com/v1/payments/{pay_id}/refund'
                                payload = {
                                    'amount': amount,
                                    "reverse_all": True
                                }
                                gateway_detail = PaymentGateway.objects.get(name='split_razorpay')
                                response = requests.post(
                                    refund_url,
                                    auth=HTTPBasicAuth(gateway_detail.gateway_key, gateway_detail.gateway_secret),
                                    data=payload
                                )

                                if response.status_code == 200:
                                    seat = order.seat
                                    seat_last_order = seat.order_set.filter(payment__status='Success').last()
                                    if seat_last_order == order:
                                        seat.is_vacent = True
                                        # run Channel Code
                                        # Update the websocket
                                        update_websocket(
                                            theatre_id=seat.row.hall.theatre.id,
                                            seat_id=seat.id,
                                            is_vacent=seat.is_vacent,
                                            payment_panding=False,
                                            seat_name=f"{seat.row.hall.name} | {seat.name}",
                                            message='Refund is Generated and It Will Transfer within 5-7 Working Days !',
                                            customer_phone=order.payment.phone_number,
                                            customer_message="✅ Refund Confirmed! %0A%0AYour refund has been successfully processed. 💸%0A%0AThe amount will be credited to your original payment method within 5–7 working days. 🏦%0A%0AThank you for your patience and for choosing Scan2Food. 🙏%0A%0AFor any queries, feel free to contact us at support@scan2food.com 📧%0A%0A— Team Scan2Food 🍿",
                                            theatre_name=seat.row.hall.theatre.name,
                                            msg_typ="refund-conformation",
                                            order_id=payment.order.pk
                                        )

                                        seat.save()

                                    payment.status = 'Refunded'
                                    order.delivery_time = localtime(timezone.now())
                                    payment.save()
                                    order.save()
                                    refund_generated = True
                                    messages.success(request, 'Refund is Generated and It Will Transfer within 5-7 Working Days !')
                                else:
                                    messages.error(request, 'No payment was collected for this Order')

                            elif payment.gateway == 'Razorpay':
                                # CODE IS WORKING AND COMPLETED FOR RAZORPAY
                                pay_id = payment.razorpaypayment.razorpay_payment_id
                                amount = payment.amount * 100
                                refund_url = f'https://api.razorpay.com/v1/payments/{pay_id}/refund'
                                payload = {
                                    'amount': amount
                                }
                                gateway_detail = PaymentGateway.objects.get(name='Razorpay')
                                response = requests.post(
                                    refund_url,
                                    auth=HTTPBasicAuth(gateway_detail.gateway_key, gateway_detail.gateway_secret),
                                    data=payload
                                )

                                if response.status_code == 200:
                                    seat = order.seat
                                    seat_last_order = seat.order_set.filter(payment__status='Success').last()
                                    if seat_last_order == order:
                                        seat.is_vacent = True
                                        # run Channel Code
                                        # Update the websocket
                                        update_websocket(
                                            theatre_id=seat.row.hall.theatre.id,
                                            seat_id=seat.id,
                                            is_vacent=seat.is_vacent,
                                            payment_panding=False,
                                            seat_name=f"{seat.row.hall.name} | {seat.name}",
                                            message='Refund is Generated and It Will Transfer within 5-7 Working Days !',
                                            customer_phone=order.payment.phone_number,
                                            customer_message="✅ Refund Confirmed! %0A%0AYour refund has been successfully processed. 💸%0A%0AThe amount will be credited to your original payment method within 5–7 working days. 🏦%0A%0AThank you for your patience and for choosing Scan2Food. 🙏%0A%0AFor any queries, feel free to contact us at support@scan2food.com 📧%0A%0A— Team Scan2Food 🍿",
                                            theatre_name=seat.row.hall.theatre.name,
                                            msg_typ="refund-conformation",
                                            order_id=payment.order.pk
                                        )

                                        seat.save()

                                    payment.status = 'Refunded'
                                    order.delivery_time = localtime(timezone.now())
                                    payment.save()
                                    order.save()
                                    refund_generated = True
                                    messages.success(request, 'Refund is Generated and It Will Transfer within 5-7 Working Days !')
                                else:
                                    messages.error(request, 'No payment was collected for this Order')

                            elif payment.gateway == 'Cashfree':
                                # CODE IS WORKING AND COMPLETED FOR CASHFREE
                                gateway_detail = PaymentGateway.objects.get(name='Cashfree')

                                Cashfree.XClientId = gateway_detail.gateway_key
                                Cashfree.XClientSecret = gateway_detail.gateway_secret
                                Cashfree.XEnvironment = Cashfree.PRODUCTION # SANDBOX or PRODUCTION
                                x_api_version = "2023-08-01"
                                order_id = payment.cashfreepayment.cashfree_order_id
                                try:
                                    # Create Refund Order
                                    refundRequest = OrderCreateRefundRequest(
                                        refund_amount=payment.amount,
                                        refund_id=f"refund_p_id_{payment.pk}"
                                    )

                                    # Refund Request
                                    api_response = Cashfree().PGOrderCreateRefund(x_api_version, order_id, refundRequest)
                                    
                                    if api_response.status_code == '200' or 200:
                                        seat = order.seat
                                        seat_last_order = seat.order_set.filter(payment__status='Success').last()

                                        if seat_last_order == order:
                                            seat.is_vacent = True
                                            # run Channel Code
                                            # Update the websocket
                                            # # update websocket
                                            update_websocket(
                                                theatre_id=seat.row.hall.theatre.id,
                                                seat_id=seat.id,
                                                is_vacent=seat.is_vacent,
                                                payment_panding=False,
                                                seat_name=f"{seat.row.hall.name} | {seat.name}",
                                                message='Refund is Generated and It Will Transfer within 5-7 Working Days !',
                                                customer_phone=order.payment.phone_number,
                                                customer_message="✅ Refund Confirmed! %0A%0AYour refund has been successfully processed. 💸%0A%0AThe amount will be credited to your original payment method within 5–7 working days. 🏦%0A%0AThank you for your patience and for choosing Scan2Food. 🙏%0A%0AFor any queries, feel free to contact us at support@scan2food.com 📧%0A%0A— Team Scan2Food 🍿",
                                                theatre_name=seat.row.hall.theatre.name,
                                                msg_typ="refund-conformation",
                                                order_id=payment.order.pk
                                            )

                                            seat.save()
                                            
                                        payment.status = 'Refunded'
                                        order.delivery_time = localtime(timezone.now())
                                        payment.save()
                                        order.save()
                                        refund_generated = True
                                        messages.success(request, 'Refund is Generated and It Will Transfer within 5-7 Working Days !')

                                    else:
                                        pass

                                except:
                                    messages.error(request, 'No payment was collected for this Order or Refund is Already Generated it may be refunded in 2-3 days in Account')

                            elif payment.gateway == 'Phonepe':
                                # CODE IS PENDING FOR PHONEPE
                                selected_gateway = PaymentGateway.objects.filter(name="Phonepe").first()
                                client_id = selected_gateway.gateway_key
                                client_secret = selected_gateway.gateway_secret
                                client_version = 1  
                                env=Env.PRODUCTION
                                client = StandardCheckoutClient.get_instance(client_id=client_id,
                                                                                    client_secret=client_secret,
                                                                                    client_version=client_version,
                                                                                    env=env)

                                # check about the payment status

                                unique_order_id = payment.phonepepayment.uu_id
                                order_response = client.get_order_status(merchant_order_id=unique_order_id)
                                order_status = order_response.state

                                if order_status == "COMPLETED":
                                    try:
                                        # PROSCEED IF PAYMENT WAS COMPLETED...
                                        unique_merchant_refund_id = f"refund-{unique_order_id}"
                                        # unique_merchant_refund_id = str(uuid4())
                                        original_merchant_order_id = unique_order_id
                                        amount = int(payment.amount * 100)
                                        
                                        refund_request = RefundRequest.build_refund_request(merchant_refund_id=unique_merchant_refund_id,
                                                                                            original_merchant_order_id=original_merchant_order_id,
                                                                                            amount=amount)
                                        refund_response = client.refund(refund_request=refund_request)

                                        refund_id = refund_response.refund_id
                                        if refund_id:
                                            seat = payment.order.seat
                                            seat_last_order = seat.order_set.filter(payment__status='Success').last()
                                            if seat_last_order == order:
                                                seat.is_vacent = True
                                                # run Channel Code
                                                # Update the websocket
                                                update_websocket(
                                                    theatre_id=seat.row.hall.theatre.id,
                                                    seat_id=seat.id,
                                                    is_vacent=seat.is_vacent,
                                                    payment_panding=False,
                                                    seat_name=f"{seat.row.hall.name} | {seat.name}",
                                                    message='Refund is Generated and It Will Transfer within 5-7 Working Days !',
                                                    customer_phone=order.payment.phone_number,
                                                    customer_message="✅ Refund Confirmed! %0A%0AYour refund has been successfully processed. 💸%0A%0AThe amount will be credited to your original payment method within 5–7 working days. 🏦%0A%0AThank you for your patience and for choosing Scan2Food. 🙏%0A%0AFor any queries, feel free to contact us at support@scan2food.com 📧%0A%0A— Team Scan2Food 🍿",
                                                    theatre_name=seat.row.hall.theatre.name,
                                                    msg_typ="refund-conformation",
                                                    order_id=payment.order.pk
                                                )

                                                seat.save()

                                                order.delivery_time = localtime(timezone.now())
                                                order.save()

                                            payment.status = 'Refunded'
                                            payment.save()
                                            phonepe_payment = payment.phonepepayment
                                            phonepe_payment.refund_id = refund_id
                                            phonepe_payment.save()
                                            refund_generated = True
                                            messages.success(request, 'Refund is Generated and It Will Transfer within 5-7 Working Days !')

                                    except Exception as e:
                                        messages.error(request, "This Payment May be already Refunded or No Payment was Collected for this Order !")


                            elif payment.gateway == 'CCAvenue':
                                # CODE IS PENDING FOR CCAvenue
                                pass

                            elif payment.gateway == 'PayU':
                                selected_gateway = PaymentGateway.objects.get(name='PayU')
                                gateway_key = selected_gateway.gateway_key
                                order_id = payment.payupayment.uu_id
                                gateway_salt = selected_gateway.gateway_salt
                                
                                # check whether the payment is successfull or not if the payment is successfull then only prosceed the work...
                                url = "https://info.payu.in/merchant/postservice.php?form=2"
                                
                                # hash to check the payment status
                                hash_string = f"{gateway_key}|verify_payment|{order_id}|{gateway_salt}"
                                hashh = hashlib.sha512(hash_string.encode('utf-8')).hexdigest()

                                payload = {
                                    "key": gateway_key,
                                    "command": "verify_payment",
                                    "var1": order_id,
                                    "hash": hashh
                                }

                                response = requests.post(url, data=payload)
                                response_data = response.json()

                                status = response_data['transaction_details'][order_id]['status']

                                if status == 'success':
                                    # Payment is success now try to refund the amount
                                    command = "cancel_refund_transaction"
                                    mihpayid = response_data['transaction_details'][order_id]['mihpayid']  # ✅ MUST be PayU's transaction ID
                                    amount = payment.amount

                                    # Hash format for refund
                                    # correct hash format: key|command|var1|salt
                                    hash_string = f"{gateway_key}|{command}|{mihpayid}|{gateway_salt}"
                                    hashh = hashlib.sha512(hash_string.encode("utf-8")).hexdigest()
                                    url = "https://info.payu.in/merchant/postservice?form=2"

                                    payload = {
                                        "key": gateway_key,
                                        "command": command,
                                        "var1": mihpayid,     # ✅ Must be mihpayid, NOT order_id
                                        "var2": order_id,
                                        "var3": amount,
                                        "var5": "https://www.scan2food.com/payu-webhook-url",
                                        "hash": hashh
                                    }

                                    response = requests.post(url, data=payload)
                                    response_data = response.json()
                                    if response_data['status'] == 1:
                                        refund_generated = True
                                        messages.success(request, response_data['msg'])
                                        seat = order.seat
                                        seat_last_order = seat.order_set.filter(payment__status='Success').last()
                                        if seat_last_order == order:
                                            seat.is_vacent = True
                                            seat.save()


                                        update_websocket(
                                            theatre_id=seat.row.hall.theatre.id,
                                            seat_id=seat.id,
                                            is_vacent=seat.is_vacent,
                                            payment_panding=False,
                                            seat_name=f"{seat.row.hall.name} | {seat.name}",
                                            message='Refund is Generated and It Will Transfer within 5-7 Working Days !',
                                            customer_phone=order.payment.phone_number,
                                            customer_message="✅ Refund Confirmed! %0A%0AYour refund has been successfully processed. 💸%0A%0AThe amount will be credited to your original payment method within 5–7 working days. 🏦%0A%0AThank you for your patience and for choosing Scan2Food. 🙏%0A%0AFor any queries, feel free to contact us at support@scan2food.com 📧%0A%0A— Team Scan2Food 🍿",
                                            theatre_name=seat.row.hall.theatre.name,
                                            msg_typ="refund-conformation",
                                            order_id=payment.order.pk
                                        )

                                        payment.status = 'Refunded'
                                        order.delivery_time = localtime(timezone.now())
                                        payment.save()
                                        order.save()

                                        # refund is initiated in queue and will be refunded in some time...
                                    else:
                                        if 'Refund FAILURE' in response_data['msg']:
                                            payment.status = 'Refunded'
                                            order.delivery_time = localtime(timezone.now())
                                            payment.save()
                                            order.save()
                                        messages.error(request, response_data['msg'])

                                else:
                                    # Payment is Not Completed Yet...
                                    messages.error(request, 'Payment is not Completed Yet. So Not able to Refund the amount !')
                                    
                            payment.reason = reason
                            payment.save() 
                            
                            if refund_generated == True:
                                send_whatsapp_template(phone_number=payment.phone_number, msg_typ='refund-conformation')

                        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

                    else:
                        messages.error(request, 'payment was collected via Cash so no refund is possible')
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
                else:
                    messages.error(request, 'Payment is Already Sorted and Send to the Theatre Owner !')
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

            else:
                messages.error(request, 'Wrong OTP Entered !')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        except:
            raise Http404('page not foud')
        
    else:
        return HttpResponse('Permission Denied')

@login_required
def partial_refund_order(request, pk):
    if request.method == 'POST':
        try:
            otp = request.POST.get('otp')
            reason = request.POST.get('reason')
            refund_items = request.POST.get('items-to-refund')
            
            refund_data = json.loads(refund_items)

            refund_amount = 0
            order = Order.objects.get(pk=pk)
            item_name_list = ""
            for item in refund_data:
                food_item = FoodItem.objects.get(pk=item['id'])
                quantity = item['quantity']
                item_name_list += f"{food_item.name}, "

                item_price = food_item.price

                add_amount = item_price * quantity
                
                refund_amount += add_amount
            
            order_food_items = order.items.all()

            payment = order.payment
        
            if order.refund_otp == otp:
                
                if payment.payout == None:
                    if payment.payment_method == 'Gateway':
                        
                        if payment.status == 'Refunded':
                            messages.error(request, 'Payment has already been settled and cannot be refunded.')

                        else:
                            refund_generated = False
                            if payment.gateway == "split_razorpay":
                                # CODE IS WORKING AND COMPLETED FOR SPLIT RAZORPAY
                                pay_id = payment.splitrazorpaypayment.razorpay_payment_id
                                amount = refund_amount * 100
                                refund_url = f'https://api.razorpay.com/v1/payments/{pay_id}/refund'
                                payload = {
                                    'amount': amount,
                                    "reverse_all": True
                                }
                                gateway_detail = PaymentGateway.objects.get(name='split_razorpay')
                                response = requests.post(
                                    refund_url,
                                    auth=HTTPBasicAuth(gateway_detail.gateway_key, gateway_detail.gateway_secret),
                                    data=payload
                                )

                                if response.status_code == 200:

                                    refund_generated = True
                                    messages.success(request, 'Refund is Generated and It Will Transfer within 5-7 Working Days !')
                                else:
                                    messages.error(request, 'No payment was collected for this Order')

                            elif payment.gateway == 'Razorpay':
                                # CODE IS WORKING AND COMPLETED FOR RAZORPAY
                                pay_id = payment.razorpaypayment.razorpay_payment_id
                                amount = refund_amount * 100
                                refund_url = f'https://api.razorpay.com/v1/payments/{pay_id}/refund'
                                payload = {
                                    'amount': amount
                                }
                                gateway_detail = PaymentGateway.objects.get(name='Razorpay')
                                response = requests.post(
                                    refund_url,
                                    auth=HTTPBasicAuth(gateway_detail.gateway_key, gateway_detail.gateway_secret),
                                    data=payload
                                )

                                if response.status_code == 200:
                                    
                                    refund_generated = True
                                    messages.success(request, 'Refund is Generated and It Will Transfer within 5-7 Working Days !')
                                else:
                                    messages.error(request, 'No payment was collected for this Order')

                            elif payment.gateway == 'Cashfree':
                                # CODE IS WORKING AND COMPLETED FOR CASHFREE
                                gateway_detail = PaymentGateway.objects.get(name='Cashfree')

                                Cashfree.XClientId = gateway_detail.gateway_key
                                Cashfree.XClientSecret = gateway_detail.gateway_secret
                                Cashfree.XEnvironment = Cashfree.PRODUCTION # SANDBOX or PRODUCTION
                                x_api_version = "2023-08-01"
                                order_id = payment.cashfreepayment.cashfree_order_id
                                try:
                                    # Create Refund Order
                                    refundRequest = OrderCreateRefundRequest(
                                        refund_amount=refund_amount,
                                        refund_id=f"refund_p_id_{payment.pk}"
                                    )

                                    # Refund Request
                                    api_response = Cashfree().PGOrderCreateRefund(x_api_version, order_id, refundRequest)
                                    
                                    if api_response.status_code == '200' or 200:
                                        
                                        refund_generated = True
                                        messages.success(request, 'Refund is Generated and It Will Transfer within 5-7 Working Days !')

                                    else:
                                        pass

                                except:
                                    messages.error(request, 'No payment was collected for this Order or Refund is Already Generated it may be refunded in 2-3 days in Account')

                            elif payment.gateway == 'Phonepe':
                                # CODE IS PENDING FOR PHONEPE
                                selected_gateway = PaymentGateway.objects.filter(name="Phonepe").first()
                                client_id = selected_gateway.gateway_key
                                client_secret = selected_gateway.gateway_secret
                                client_version = 1  
                                env=Env.PRODUCTION
                                client = StandardCheckoutClient.get_instance(client_id=client_id,
                                                                                    client_secret=client_secret,
                                                                                    client_version=client_version,
                                                                                    env=env)

                                # check about the payment status

                                unique_order_id = payment.phonepepayment.uu_id
                                order_response = client.get_order_status(merchant_order_id=unique_order_id)
                                order_status = order_response.state

                                if order_status == "COMPLETED":
                                    try:
                                        # PROSCEED IF PAYMENT WAS COMPLETED...
                                        unique_merchant_refund_id = f"refund-{unique_order_id}"
                                        # unique_merchant_refund_id = str(uuid4())
                                        original_merchant_order_id = unique_order_id
                                        amount = int(payment.amount * 100)
                                        
                                        refund_request = RefundRequest.build_refund_request(merchant_refund_id=unique_merchant_refund_id,
                                                                                            original_merchant_order_id=original_merchant_order_id,
                                                                                            amount=amount)
                                        refund_response = client.refund(refund_request=refund_request)

                                        refund_id = refund_response.refund_id
                                        if refund_id:
                                            refund_generated = True
                                            messages.success(request, 'Refund is Generated and It Will Transfer within 5-7 Working Days !')

                                    except Exception as e:
                                        messages.error(request, "This Payment May be already Refunded or No Payment was Collected for this Order !")


                            elif payment.gateway == 'CCAvenue':
                                # CODE IS PENDING FOR CCAvenue
                                pass

                            elif payment.gateway == 'PayU':
                                selected_gateway = PaymentGateway.objects.get(name='PayU')
                                gateway_key = selected_gateway.gateway_key
                                order_id = payment.payupayment.uu_id
                                gateway_salt = selected_gateway.gateway_salt
                                
                                # check whether the payment is successfull or not if the payment is successfull then only prosceed the work...
                                url = "https://info.payu.in/merchant/postservice.php?form=2"
                                
                                # hash to check the payment status
                                hash_string = f"{gateway_key}|verify_payment|{order_id}|{gateway_salt}"
                                hashh = hashlib.sha512(hash_string.encode('utf-8')).hexdigest()

                                payload = {
                                    "key": gateway_key,
                                    "command": "verify_payment",
                                    "var1": order_id,
                                    "hash": hashh
                                }

                                response = requests.post(url, data=payload)
                                response_data = response.json()

                                status = response_data['transaction_details'][order_id]['status']

                                if status == 'success':
                                    # Payment is success now try to refund the amount
                                    command = "cancel_refund_transaction"
                                    mihpayid = response_data['transaction_details'][order_id]['mihpayid']  # ✅ MUST be PayU's transaction ID
                                    amount = refund_amount

                                    # Hash format for refund
                                    # correct hash format: key|command|var1|salt
                                    hash_string = f"{gateway_key}|{command}|{mihpayid}|{gateway_salt}"
                                    hashh = hashlib.sha512(hash_string.encode("utf-8")).hexdigest()
                                    url = "https://info.payu.in/merchant/postservice?form=2"

                                    payload = {
                                        "key": gateway_key,
                                        "command": command,
                                        "var1": mihpayid,     # ✅ Must be mihpayid, NOT order_id
                                        "var2": order_id,
                                        "var3": amount,
                                        "var5": "https://www.scan2food.com/payu-webhook-url",
                                        "hash": hashh
                                    }

                                    response = requests.post(url, data=payload)
                                    response_data = response.json()
                                    if response_data['status'] == 1:
                                        refund_generated = True
                                        messages.success(request, response_data['msg'])
                                        # refund is initiated in queue and will be refunded in some time...
                                    
                                    else:
                                        if 'Refund FAILURE' in response_data['msg']:
                                            payment.status = 'Refunded'
                                            order.delivery_time = localtime(timezone.now())
                                            payment.save()
                                            order.save()
                                        messages.error(request, response_data['msg'])

                                else:
                                    # Payment is Not Completed Yet...
                                    messages.error(request, 'Payment is not Completed Yet. So Not able to Refund the amount !')
                            
                            if refund_generated == True:
                                for item in refund_data:
                                    order_item = order_food_items.filter(food_item_id=item['id']).first()
                                    if order_item.quantity == item['quantity']:
                                        # delete the item
                                        order_item.delete()

                                    else:
                                        order_item.quantity -= item['quantity']
                                        order_item.save()

                                payment.reason = reason
                                payment.amount = payment.amount - refund_amount
                                
                                payment.save()

                                send_whatsapp_template(phone_number=payment.phone_number, msg_typ='partial-refund-conformation', items=item_name_list, refund_amount=refund_amount)

                        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

                    else:
                        messages.error(request, 'payment was collected via Cash so no refund is possible')
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
                else:
                    messages.error(request, 'Payment is Already Sorted and Send to the Theatre Owner !')
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

            else:
                messages.error(request, 'Wrong OTP Entered !')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        except Exception as e:
            return HttpResponse(f'Error Occured: {e}')
            # raise Http404('page not foud')
        
    else:
        return HttpResponse('Permission Denied')

def invoice(request, pk):
    try:
        order = Order.objects.get(pk=pk)
        total_amount = order.payment.amount - order.full_payment()
        total_amount = round(total_amount, 2)
        taxable_amount = total_amount / 1.18
        taxable_amount = round(taxable_amount, 2)
        cgst = total_amount - taxable_amount
        gst = cgst
        cgst = cgst / 2
        cgst = round(cgst, 2)
        sgst = cgst
        igst = 0.00
        cgst_per = 9
        igst_per = 0

        if order.payment.invoice_comp == 'DOP AGENT SOFTWARE':
            try:
                if order.seat.row.hall.theatre.gstdetails.gst_state != "Karnataka":
                    igst = cgst * 2
                    igst = round(igst, 2)
                    sgst = 0.00
                    cgst = 0.00
                    cgst_per = 0
                    igst_per = 18
                    gst = igst
            except:
                pass
            gst = round(gst, 2)
            context = {'order': order, "taxable_amount": taxable_amount, "total_amount": total_amount, "cgst": cgst, "sgst": sgst, "igst": igst, "gst": gst, 'cgst_per': cgst_per, 'igst_per': igst_per}
            return render(request, 'theatre/invoice.html', context)

        else:
            try:
                gst_state = order.seat.row.hall.theatre.gstdetails.gst_state
                if order.pk == 52156:
                    gst_state = 'HARYANA'
                elif gst_state != "Haryana":
                    igst = cgst * 2
                    igst = round(igst, 2)
                    sgst = 0.00
                    cgst = 0.00
                    cgst_per = 0
                    igst_per = 18
                    gst = igst
            except:
                pass
            gst = round(gst, 2)
            context = {'order': order, "taxable_amount": taxable_amount, "total_amount": total_amount, "cgst": cgst, "sgst": sgst, "igst": igst, "gst": gst, 'cgst_per': cgst_per, 'igst_per': igst_per}
            return render(request, 'theatre/invoice2.html', context)

    except:
        raise Http404('Page not found...')
    
def sign_up(request):
    if request.method == 'POST':
        form = SignUp(request.POST)
        if form.is_valid():
            theatre_name = form.cleaned_data['theatre_name']
            owner_name = form.cleaned_data['owner_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                # CREATE A THEATRE
                theatre = Theatre.objects.create(
                    name=theatre_name,
                    owner_name = owner_name,
                    phone_number = phone_number,
                    email=email
                )

                # CREATE FOOD CATEGORY FOR THEATRE
                food_catogaries = [
                    FoodCategory(name='Popcorn', theatre=theatre),
                    FoodCategory(name='Beverages', theatre=theatre),
                    FoodCategory(name='Combos', theatre=theatre),
                    FoodCategory(name='Fast Food', theatre=theatre),
                    FoodCategory(name='Patty', theatre=theatre),
                ]

                # Bulk create
                FoodCategory.objects.bulk_create(food_catogaries)

                # CREATE DETAIL OF THEATRE IN ADMIN PORTAL
                detail = Detail.objects.create(
                    theatre=theatre,
                )

                # CREATE A NEW USER
                user = User.objects.create(
                    username=phone_number,
                    password=make_password(password),
                    first_name=owner_name,
                )

                # CREATE Commission ENTITY OF THEATRE
                Commission.objects.create(theatre=theatre, commission_perscantage=5.0)

                # GET THE GROUP
                user_type = 'admin'
                group = Group.objects.filter(name=user_type).first()

                # CREATING THE USER PROFILE PAGE
                UserProfile.objects.create(user=user, theatre=theatre)

                # ADDING THE USER TO THE GROUP
                user.groups.add(group)

                # return a success message
                messages.success(request, 'New Theare is Created Update the Details of Your Theatre')

                return redirect('theatre:theatre-detail')
            
            except IntegrityError as e:
                messages.error(request, f'UserId {phone_number} is Alrady There So create user with another User Id')

                return redirect('theatre:sign-up')

    form = SignUp()
    return render(request, 'theatre/sign-up.html', {'form': form})

def raise_refund_request(request, pk):
    if request.method == 'POST':
        phone_number = request.POST.get('phone-number')

        try:
            refund_request = OrderRefundRequest.objects.filter(order_id=pk).first()
            if refund_request == None:
                raise KeyError
        except:
            order = Order.objects.get(pk=pk)
            customer_mobile = order.payment.phone_number

            if phone_number in customer_mobile:
                # CREATE THE REFUND REQUEST
                
                refund_request = OrderRefundRequest.objects.create(order=order)
                refund_request.save()
                
                # SEND WHATSAPP MESSAGE
                send_whatsapp_template(
                    msg_typ="raise-refund-request",
                    phone_number=customer_mobile, 
                    refund_amount=order.payment.amount,
                    theatre_name=order.seat.row.hall.theatre.name,
                    order_id=order.pk
                    )
                
                cache_key = f'refund-query-id-{refund_request.order.seat.row.hall.theatre.id}'
                cache.delete(cache_key)
                cache_key = 'all-refund-query-count'
                cache.delete(cache_key)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def all_refund_queries(request):
    if user_has_permission(request.user, "view_order"):
        theatre = request.user.userprofile.theatre
        date_range = request.GET.get('daterange', "")
        resolve_status = request.GET.get('resolve_status', "")

        if date_range == "":
            start_date = localtime(timezone.now()).date()
            end_date = localtime(timezone.now()).date()
        else:
            try:
                start_date = date_range.split(" - ")[0]
                end_date = date_range.split(" - ")[1]

                start_date = datetime.strptime(start_date, "%d/%b/%Y").date()
                end_date = datetime.strptime(end_date, "%d/%b/%Y").date()
            except:
                start_date = localtime(timezone.now()).date()
                end_date = localtime(timezone.now()).date()

        refund_queries = OrderRefundRequest.objects.filter(order__seat__row__hall__theatre=theatre, time__date__range=(start_date, end_date))
        refund_queries = refund_queries.order_by('-time')

        if resolve_status == "resolved":
            refund_queries = refund_queries.filter(resolve_status=True)
            
        elif resolve_status == "not-resolved":
            refund_queries = refund_queries.filter(resolve_status=False)
            
        paginator = Paginator(refund_queries, 10)  # Show 10 items per page.

        page_number = request.GET.get('page')
        if page_number == None:
            page_number = 1

        refund_queries = paginator.get_page(page_number)

        context = {
            'refund_queries': refund_queries,
            'start_date': start_date,
            'end_date': end_date,
            'resolve_status': resolve_status
            }
            
        return render(request, 'theatre/all-refund-queries.html', context)
    else:
        return HttpResponse('Permission Denied')