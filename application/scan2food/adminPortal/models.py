from django.db import models
from theatre.models import Theatre
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


# Create your models here.
# Admin Users Profiles
class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    active_status = models.BooleanField(default=True)
    
    def __str__(self) -> str:
        return self.user.first_name
    
# Theatre Payout Logs
class PayOutLogs(models.Model):
    theatre = models.ForeignKey(Theatre, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    generated_time = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='issue_by', null=True, blank=True)
    is_settled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.generated_time} Start time ===> { self.start_time} end_time ===>{ self.end_time}"

# PAYMENT GATEWAYS FOR ALL THE GATEWAYS
class PaymentGateway(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False, unique=True)
    gateway_key = models.CharField(max_length=100, null=False, blank=False)
    gateway_secret = models.CharField(max_length=100, null=False, blank=False)
    gateway_salt = models.CharField(max_length=100, null=True, blank=True)
    merchant_id = models.CharField(max_length=100, null=True, blank=True)
    access_code = models.CharField(max_length=100, null=True, blank=True)
    working_key = models.CharField(max_length=100, null=True, blank=True)
 
    is_active = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name

# Theatre Other Details
class Detail(models.Model):
    PAYMENT_MODEL =[
        ('theatre', 'Theatre'),
        ('customer', 'Customer'),
    ]

    SETTLEMENT_MODEL = [
        ('Manual', 'Manual'),
        ('Split', 'Split'),
    ]

    theatre = models.OneToOneField(Theatre, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    expire_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    secondary_mobile = models.CharField(max_length=100, default="")
    break_start_time = models.TimeField(default=None, null=True, blank=True)
    scaning_service = models.BooleanField(default=True)
    payment_model = models.CharField(max_length=10, choices=PAYMENT_MODEL, default='customer')
    settlement_model = models.CharField(max_length=10, choices=SETTLEMENT_MODEL, default="Manual")
    razorpay_id = models.CharField(max_length=100, default="", null=True, blank=True)
    logo = models.ImageField(upload_to='theatre_logo/', default="theatre_logo/default.png")
    selected_gateway = models.ForeignKey(PaymentGateway, on_delete=models.SET_NULL, default="", blank=True, null=True)

    # ADDITIONAL FIELDS FOR BETTER INTEGRATION OF CCAVANUE PAYMENT GATEWAY
    # WE GET STATE FROM GST DETAILS
    state = models.CharField(max_length=100, default="Haryana")
    city = models.CharField(max_length=100, default="")
    zip = models.CharField(max_length=20, default="")


    def __str__(self) -> str:
        return self.theatre.name
    
    def save(self, *args, **kwargs):
        if not self.expire_date:
            self.expire_date = timezone.now() + timedelta(days=30)
        super().save(*args, **kwargs)
    
    def commission(self):
        commission = self.theatre.commission_set.last()
        if commission == None:
            return 5.0
        else:
            return commission.commission_perscantage
        
class bankDetails(models.Model):
    theatre = models.OneToOneField(Theatre, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=100, default="")
    account_name = models.CharField(max_length=100, default="")
    ifsc_code = models.CharField(max_length=100, default="")
    bank_name = models.CharField(max_length=100, default="")
    branch_name = models.CharField(max_length=100, default="")

    def __str__(self) -> str:
        return self.theatre.name
    
class GSTDetails(models.Model):
    theatre = models.OneToOneField(Theatre, on_delete=models.CASCADE)
    gst_number = models.CharField(max_length=100, default="")
    pan = models.CharField(max_length=100, default="")
    gst_state = models.CharField(max_length=100, default="")
    state_code = models.CharField(max_length=100, default="")
    gst_address = models.CharField(max_length=500, default="")
    firm_name = models.CharField(max_length=100, default="")

    def __str__(self) -> str:
        return self.theatre.name

# Theatre Documents Folder Location
def document_upload_path(instance, filename):
    # folder will be: documents/<theatre_id>/filename
    return f'documents/{instance.theatre.pk}/{filename}'


class Documents(models.Model):

    theatre = models.ForeignKey(Theatre, on_delete=models.CASCADE)
    document_name = models.CharField(max_length=100)
    document = models.FileField(upload_to=document_upload_path)
    is_verified = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.document_name


class Commission(models.Model):
    theatre = models.ForeignKey(Theatre, on_delete=models.CASCADE)
    commission_perscantage = models.FloatField(default=5)

    def __str__(self):
        return f"{self.theatre.name} | {self.commission_perscantage}%"

class Query(models.Model):
    name = models.CharField(max_length=100, blank=False)
    email = models.EmailField(max_length=100, blank=False)
    phone = models.CharField(max_length=15, blank=False)
    place = models.CharField(max_length=100, blank=False)
    description = models.CharField(max_length=2000, blank=False)
    time = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False, blank=False, null=False)

    def __str__(self):
        return f"{self.name} | {self.email}"