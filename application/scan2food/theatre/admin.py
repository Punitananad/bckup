from django.contrib import admin
from .models import *
from django.db.models import Count
from django.utils.html import format_html

# Register your models here.
@admin.register(Row)
class RowAdmin(admin.ModelAdmin):
    list_display = ('name', 'hall_name', 'theatre_name', 'seat_count')
    list_filter = ('hall', 'hall__theatre')
    search_fields = ('name', 'hall__name', 'hall__theatre__name')
    ordering = ('hall', ) 

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_seat_count=Count("seat"))

    def seat_count(self, obj):
        return obj._seat_count
    seat_count.short_description = "Seat Count"
    seat_count.admin_order_field = "_seat_count"  # 🔥 enables sorting

    def hall_name(self, obj):
        return obj.hall.name
    hall_name.short_description = "Hall"
    hall_name.admin_order_field = "hall__name"  # 🔥 enables sorting
    
    def theatre_name(self, obj):
        return obj.hall.theatre.name
    theatre_name.short_description = "Theatre"
    theatre_name.admin_order_field = "hall__theatre__name"  # enable sorting🔥

@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ('name', 'theatre_name', 'seat_count')
    search_fields = ('name', 'theatre__name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(total_seats=Count("row__seat"))
        return qs
    
    def theatre_name(self, obj):
        return obj.theatre.name
    theatre_name.short_description = 'Theatre'
    theatre_name.admin_order_field = 'theatre__name'
    
    def seat_count(self, obj):
        return obj.total_seats
    
    seat_count.short_description = 'Seats'
    seat_count.admin_order_field = 'total_seats'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'order_id', 'amount', 'time', 'theatre_name', 'payment_method', 'status', 'gateway', 'is_settled')
    search_fields = ('pk', 'order__pk', 'order__seat__row__hall__theatre__name')

    def order_id(self, obj):
        return format_html(
            '<a href="/admin/theatre/order/{}/change/" target="_blank">{}</a>',
            obj.order.pk,
            obj.order.pk,   
        )
    
    def theatre_name(self, obj):
        return obj.order.seat.row.hall.theatre.name
    theatre_name.short_description = 'Theatre'
    theatre_name.admin_order_field = 'order__seat__row__hall__theatre__name'

@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'theatre', 'fooditem_count')
    list_filter = ('theatre', )

    search_fields = ('name', 'theatre')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(_fooditem_count=Count("fooditem"))

    def fooditem_count(self, obj):
        return obj._fooditem_count
    
    fooditem_count.short_description = "Food Items"
    fooditem_count.admin_order_field = "_fooditem_count"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'theatre_name', 'seat_name', 'payment_status', 'total_amount')

    def theatre_name(self, obj):
        return obj.seat.row.hall.theatre.name
    theatre_name.short_description = "Theatre"
    theatre_name.admin_order_field = "seat__row__hall__theatre__name"

    def payment_status(self, obj):
        if obj.payment.status == 'Success':
            return_html = format_html(
                '<img src="/static/admin/img/icon-yes.svg">'
            )
        elif obj.payment.status == 'Refunded':
            return_html = format_html(
                '<img src="/static/admin/img/icon-alert.svg" alt="False">'
            )
        elif obj.payment.status == 'Created':
            return_html = format_html(
                '<img src="/static/admin/img/icon-no.svg">'
            )
        return return_html
    payment_status.shor_description = 'Payment Status'
    payment_status.admin_order_field = 'payment__status'

    def total_amount(self, obj):
        return obj.order_amount()
    total_amount.short_description = 'Total Amount'
    total_amount.admin_order_field = 'payment__amount'

    def seat_name(self, obj):
        return f"{obj.seat.row.hall.theatre.name} | {obj.seat.row.hall.name}({obj.seat.name})"
    seat_name.short_description = "Seat"
    seat_name.admin_order_field = "seat"
    
@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'food_type', 'price', 'catogary_name', 'theatre', 'is_available')
    list_filter = ('catogary', 'catogary__theatre')
    search_fields = ('name', 'food_type', 'catogary__name', 'catogary__theatre__name')

    def theatre(self, obj):
        return obj.catogary.theatre.name
    theatre.short_description = 'Theatre Name'
    theatre.admin_order_field = 'catogary__theatre'

    def catogary_name(self, obj):
        return obj.catogary.name
    catogary_name.short_description = 'CATOGARY'
    catogary_name.admin_order_field = 'catogary__name'


admin.site.register(PhonepePayment)
admin.site.register(Discount)
admin.site.register(PayuPayment)

admin.site.register(RazorpayPayment)
admin.site.register(SplitRazorpayPayment)
admin.site.register(OrderRefundRequest)

@admin.register(Theatre)
class TheatreAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner_name', 'address', 'phone_number', 'email', 'user')
    search_fields = ('name', 'owner_name', 'phone_number', 'email')
    list_filter = ('address', )

    def user(self, obj):
        return format_html(
            '<a href="/admin/auth/user/{}/change/">{}</a>',
            obj.userprofile_set.first().user.id,
            obj.userprofile_set.first().user.username,
        )
    
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'first_name',
        'login_id',
        'designation',
        'theatre',
        'active_status',
        )
    search_fields = ('user__username', 'theatre__name', 'active_status')
    list_filter = ('theatre', 'active_status')

    def first_name(self, obj):
        return obj.user.first_name
    
    def designation(self, obj):
        return obj.user.groups.first().name if obj.user.groups.exists() else 'No Designation'

    def login_id(self, obj):
        return obj.user.username