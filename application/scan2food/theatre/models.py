from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime as dt

# Create your models here.
class Theatre(models.Model):
    name = models.CharField(max_length=200)
    owner_name = models.CharField(max_length=200)
    address = models.TextField()
    phone_number = models.CharField(max_length=15, blank=True, default="")
    otp_phone_number = models.CharField(max_length=10, blank=True, default="")
    otp_person_name = models.CharField(max_length=50, blank=True, default="")
    otp = models.CharField(max_length=4, blank=True, default="")
    otp_time = models.DateTimeField(blank=True, null=True, default=None)  # Time when OTP was generated
    service_end_time = models.TimeField(default=dt.time(23, 45))  # Time when the service ends
    
    email = models.EmailField(max_length=50, blank=False, default="")
    notification_numbers = models.CharField(max_length=21, blank=True, default="")
    query_number = models.CharField(max_length=10, blank=True, default="")

    order_limit = models.IntegerField(default=25)  # max Limit of number of orders at a time
    cash_activated = models.BooleanField(default=False) # if cash activated then user can order from the cash also

    download_invoice = models.BooleanField(default=True) # can download the invoice
    group = models.CharField(max_length=200, default="")

    def __str__(self):
        return self.name
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    theatre = models.ForeignKey(Theatre, on_delete=models.CASCADE)
    active_status = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.user.username

class FoodCategory(models.Model):
    name = models.CharField(max_length=100)
    theatre = models.ForeignKey(Theatre, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.name}"

class FoodItem(models.Model):
    FOOD_TYPE = [
        ('veg', 'Veg'),
        ('non-veg', 'Non-Veg'),
    ]
    MADE_BY = [
        ('packaged', 'Packaged'),
        ('in-house', 'In House'),
        ('third-party', 'Third Party'),
    ]
    UNAVAILABLE_BY = [
        ('auto', 'Auto'),
        ('manual', 'Manual'),
    ]
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.IntegerField(default=1)
    food_type = models.CharField(max_length=20, choices=FOOD_TYPE)
    
    made_by = models.CharField(max_length=15, choices=MADE_BY, default='in-house')
    unavailable_by = models.CharField(max_length=15, choices=UNAVAILABLE_BY, default='auto')
    
    catogary = models.ForeignKey(FoodCategory, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    food_image = models.ImageField(default='default_food_img.png', upload_to='food_images')
    priority_number = models.IntegerField(default=1)
    min_time = models.IntegerField(default=5)
    max_time = models.IntegerField(default=30)

    is_approved = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name
    
    def discounted_price(self):
        try:
            discount_perscentage = self.catogary.theatre.discount.discount_perscantage
        except:
            discount_perscentage = 0

        discounted_price = self.price + (self.price * discount_perscentage / 100)
        discounted_price = round(discounted_price, 2)
        
        return discounted_price

    class Meta:
        ordering = ['priority_number']

class Tax(models.Model):
    name = models.CharField(max_length=100)
    percentage = models.FloatField()
    theatre = models.ForeignKey(Theatre, on_delete=models.CASCADE)

class Hall(models.Model):
    name = models.CharField(max_length=100)
    theatre = models.ForeignKey(Theatre, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} | {self.theatre.name}"

class Row(models.Model):
    name = models.CharField(max_length=10)
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.name} | {self.hall} | {self.hall.theatre.name}"

class Seat(models.Model):
    name = models.CharField(max_length=100)
    row = models.ForeignKey(Row, on_delete=models.CASCADE)
    is_vacent = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name
    
# orders
class Order(models.Model):
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, null=True)
    start_time = models.DateTimeField(auto_now_add=True)
    delivery_time = models.DateTimeField(blank=True, null=True)

    refund_otp = models.CharField(max_length=6, blank=True, null=True, default=None) # OTP for refunding the order
    otp_timing = models.DateTimeField(blank=True, null=True)
    is_shown = models.BooleanField(default=False) # if the order is shown to the user or not
    
    # order slug
    # SLUG STYLE =====> |24:year|09:mon|22:day|16:hour|18:min|1:restorent-id|23:seat-id|-extra part|245:order-no| =======> 2409221618123-245
    order_slug = models.SlugField(max_length=100, default="")

    # going to create the logs
    taken_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='taken_by')
    delivered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='delivered_by')

    chatuser = models.ForeignKey('chat_box.chatuser', on_delete=models.SET_NULL, null=True, blank=True)

    notes = models.TextField(null=True, blank=True, default="")
    
    rating = models.IntegerField(default=0, null=True, blank=True)
    comment = models.TextField(null=True, blank=True, default="")

    review_done = models.BooleanField(default=False)

    def get_gateway_order_id(self):
        payment = self.payment
        if payment.gateway == 'Razorpay':
            return payment.razorpaypayment.razorpay_payment_id
        elif payment.gateway == 'CashFree':
            return payment.cashfreepayment.cashfree_order_id
        elif payment.gateway == 'PhonePe':
            return payment.phonepepayment.order_id
        elif payment.gateway == 'CCAvenue':
            return payment.ccavenuepayment.uu_id
        elif payment.gateway == 'PayU':
            return payment.payupayment.order_id
        elif payment.gateway == 'split_razorpay':
            return payment.splitrazorpaypayment.razorpay_payment_id
        else:
            return None
        

    def generate_slug(self):
        now = timezone.localtime(timezone.now())
        start_date = now.date()
        end_date = now.date()
        seat = self.seat
        theatre = seat.row.hall.theatre
        todays_order = Order.objects.filter(seat__row__hall__theatre=theatre, start_time__date__range=(start_date, end_date)).count()

        year = now.strftime("%y")
        month = now.strftime("%m")
        day = now.strftime("%d")
        hour = now.strftime("%H")
        min = now.strftime("%M")
        

        slug = f"{year}{month}{day}{hour}{min}{theatre.id}{seat.id}{todays_order}"
        
        return slug


    def order_amount(self):
        all_items = self.items.all()
        total_amount = 0
        for item in all_items:
            total_amount += item.price * item.quantity
        
        total_amount -= self.payment.settlement
        return total_amount

    def full_payment(self):
        all_tax = self.seat.row.hall.theatre.tax_set.all()
        add_percentage = 0
        
        total_amount = self.order_amount()

        for tax in all_tax:
            add_percentage += tax.percentage
        
        tax_amount = total_amount * (add_percentage / 100)
        total_amount += tax_amount
        return total_amount

    def get_items(self):
        return_string = "".join([f"{item.name} * {item.quantity}, " for item in self.items.all()])
        return return_string
    
    def who_taken(self):
        if self.taken_by == None:
            return "Self"
        else:
            return self.taken_by.first_name
    
    def who_deliverd(self):
        if self.delivered_by == None:
            return ""
        else:
            return self.delivered_by.first_name

    def max_time(self):
        max_time_order = self.items.order_by('-food_item__max_time').first()
        max_time = max_time_order.food_item.max_time if max_time_order else 30
        return max_time

# refund request
class OrderRefundRequest(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    resolve_status = models.BooleanField(default=False)
    time = models.DateTimeField(auto_now_add=True)

# order items
class OrderItems(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200)
    quantity = models.IntegerField()
    price = models.FloatField()
    food_item = models.ForeignKey(FoodItem, on_delete=models.SET_NULL, null=True, blank=True)

    def item_price(self):
        return self.quantity * self.price

# Discount
class Discount(models.Model):
    discount_perscantage = models.IntegerField()
    theatre = models.OneToOneField(Theatre, on_delete=models.CASCADE)
    message = models.CharField(max_length=200, default="")
    is_valid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.theatre.name} | {self.discount_perscantage}"

# payments
class Payment(models.Model):
    COMPANY_NAME = [
        ('DOP AGENT SOFTWARE', 'DOP AGENT SOFTWARE'),
        ('SCAN2FOOD', 'SCAN2FOOD')
    ]
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    amount = models.FloatField()
    time = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=100, default='Pending')
    transaction_id = models.CharField(max_length=500, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True, default="")
    status = models.CharField(max_length=50, default='Created') #Created, Success, Refunded
    gateway = models.CharField(max_length=50, default='', null=True, blank=True) #Razorpay, CashFree
    is_settled = models.BooleanField(default=False)
    settlement = models.FloatField(default=0)

    # invoice created by
    invoice_comp = models.CharField(max_length=20, choices=COMPANY_NAME, default="SCAN2FOOD")

    # cust_gst = models.CharField(max_length=40, null=True, blank=True, default=None)

    payout = models.ForeignKey('adminPortal.PayOutLogs', on_delete=models.SET_NULL, null=True, blank=True)

    # reason if it was refunded
    reason = models.TextField(default="", null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.order.id} | {self.amount} | {self.time} | {self.payment_method} | {self.status}"
    
    def theatre_amount(self):
        return round(self.amount - self.settlement, 2)
    
# Razorpay Payments Details
class RazorpayPayment(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE)
    razorpay_order_id = models.CharField(max_length=255)
    razorpay_payment_id = models.CharField(max_length=255)
    razorpay_signature = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.payment.order.id} | {self.razorpay_order_id} | {self.razorpay_payment_id}"

# Split Razorpay Payments Details
class SplitRazorpayPayment(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE)
    razorpay_order_id = models.CharField(max_length=255)
    razorpay_payment_id = models.CharField(max_length=255)
    razorpay_signature = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.payment.order.id} | {self.razorpay_order_id} | {self.razorpay_payment_id}"


# Cashfree Payments Details
class CashFreePayment(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE)
    cashfree_order_id = models.CharField(max_length=500, unique=True, db_index=True, default="")
    payment_session_id = models.CharField(max_length=500, unique=True, default="")

# PhonePe Payment Details
class PhonepePayment(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE)
    uu_id = models.CharField(max_length=500, unique=True, db_index=True, default="") # Created by us
    order_id = models.CharField(max_length=500, unique=True, db_index=True, default="") # get by phonepe
    payment_url = models.CharField(max_length=1500, default="")
    refund_id = models.CharField(max_length=500, default="") # get by phonepe

    def __str__(self):
        return f"{self.payment.order.pk}|{self.payment.amount}"

# CCAvenue Payment Details
class CCAvenuePayment(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE)
    uu_id = models.CharField(max_length=500, unique=True, db_index=True) # Created by us order_id
    traking_id = models.CharField(max_length=500, unique=True, db_index=True) # get by CCAvenue
    bank_ref_no = models.CharField(max_length=500, unique=True, db_index=True) # get by CCAvenue

    def __str__(self):
        return f"{self.payment.order.pk}|{self.payment.amount}"

# PayU Payment Details
class PayuPayment(models.Model):
    payment = models.OneToOneField(Payment,on_delete=models.CASCADE)
    uu_id = models.CharField(max_length=500, unique=True, db_index=True) # Created by us
    order_id = models.CharField(max_length=500, unique=True, db_index=True) # get by PayU

    def __str__(self):
        return f"{self.payment.order.pk}|{self.payment.amount}"
