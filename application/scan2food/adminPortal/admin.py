from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(bankDetails)
class bankDetailAdmin(admin.ModelAdmin):
    list_display = ('theatre', 'account_name', 'account_number', 'bank_name')


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('theatre', 'commission',)
    search_fields = ('theatre__name', 'commission_perscantage')

    def commission(self, obj):
        return obj.commission_perscantage

    commission.short_description = "Commission (%)"
    commission.admin_order_field = "commission_perscantage"


# admin.site.register(Detail)
@admin.register(Detail)
class DetailAdmin(admin.ModelAdmin):
    list_display = ('theatre', 'is_active',  'payment_model', 'scaning_service')
    search_fields = ('theatre__name', )


# admin.site.register(GSTDetails)
@admin.register(GSTDetails)
class GSTDetailsAdmin(admin.ModelAdmin):
    list_display = ('theatre', 'gst_number', 'gst_state', 'state_code')
    search_fields = ('theatre__name', 'gst_number', 'gst_state', 'state_code')


# admin.site.register(PayOutLogs)
@admin.register(PayOutLogs)
class PayOutLogsAdmin(admin.ModelAdmin):
    list_display = ('theatre', 'start_time', 'end_time', 'generated_time', 'amount', 'is_settled')


# admin.site.register(PaymentGateway)
@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name', )


# admin.site.register(Query)
@admin.register(Query)
class QueryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'place', 'time', 'seen')
    search_fields = ('name', 'email', 'phone', 'place',)

# admin.site.register(AdminProfile)
@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ("first_name", "login_id", "active_status")
    
    search_fields = ("user__first_name", "user__username")

    def first_name(self, obj):
        return obj.user.first_name
    first_name.short_description = "First Name"
    first_name.admin_order_field = "user__first_name"

    def login_id(self, obj):
        return obj.user.username
    login_id.short_description = "Login Id"
    login_id.admin_order_field = "user__username"