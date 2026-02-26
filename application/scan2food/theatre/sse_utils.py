# sse_utils.py or similar

from django.utils import timezone, dateformat
from django.utils.timezone import localtime
from datetime import datetime, timedelta, time
from .models import Order, Theatre
from django.db.models import Max, Q

def get_all_orders(request):
    date_range = request.GET.get('daterange', "")
    order_status = request.GET.get('order-status')
    selected_theatre = request.GET.get('selected-theatre', "")
    seat_status = request.GET.get('seat-status', "")
    payment_id = request.GET.get('payment-id', "")
    scan2food_payment_id = request.GET.get('scan2food-payment-id', "")
    phone_number = request.GET.get('phone-number', "")
    # deactivate_theatres = Theatre.objects.filter(detail__scaning_service=False).count()

    current_time = localtime(timezone.now())
    current_time = current_time.replace(tzinfo=None)

    if date_range == "":
        start_date = timezone.now().date()
        end_date = timezone.now().date()

        if current_time.hour < 6:
            start_date = start_date - timedelta(days=1)
        else:
            end_date = end_date + timedelta(days=1)

    else:
        try:
            start_date = date_range.split(" - ")[0]
            end_date = date_range.split(" - ")[1]

            start_date = datetime.strptime(start_date, "%d/%b/%Y").date()
            end_date = datetime.strptime(end_date, "%d/%b/%Y").date()
        except:
            start_date = localtime(timezone.now()).date()
            end_date = localtime(timezone.now()).date()

            if current_time.hour < 6:
                start_date = start_date - timedelta(days=1)
            else:
                end_date = end_date + timedelta(days=1)
    
    tiem_obj = time(hour=6, minute=0, second=0, microsecond=0)
    start_time = datetime.combine(start_date, tiem_obj)
    end_time = datetime.combine(end_date, tiem_obj)

    if selected_theatre == "":
        all_orders = Order.objects.filter(start_time__range=(start_time, end_time))
    else:
        all_orders = Order.objects.filter(
            start_time__range=(start_time, end_time),
            seat__row__hall__theatre__pk=selected_theatre
        )

    if order_status is None or order_status == "":
        order_status = "Success"

    if order_status != "All":
        all_orders = all_orders.filter(payment__status=order_status)
    
    if seat_status == "Vacent":
        all_orders = all_orders.filter(seat__is_vacent=False)


        unique_seat_order_ids = (
            all_orders
            .values('seat_id')           # Group by seat
            .annotate(min_id=Max('id'))  # Pick minimum order id per seat
            .values_list('min_id', flat=True)  # Just the ids
        )



        all_orders = Order.objects.filter(id__in=unique_seat_order_ids)
        all_orders = all_orders.order_by('payment__time')

    else:
        all_orders = all_orders.order_by('-payment__time')
    
    if payment_id != "":
        all_orders = all_orders.filter(
            Q(payment__razorpaypayment__razorpay_payment_id__icontains=payment_id) |
            Q(payment__splitrazorpaypayment__razorpay_payment_id__icontains=payment_id)
            )

    if scan2food_payment_id != "":
        all_orders = all_orders.filter(payment__pk__icontains=scan2food_payment_id)

    if phone_number != "":
        # Clean phone number: remove +tel: prefix and any whitespace
        cleaned_phone = phone_number.replace("+tel:", "").replace(" ", "").strip()
        all_orders = all_orders.filter(payment__phone_number__icontains=cleaned_phone)

    return list(all_orders)
