from django.contrib import admin
from .models import *


# Register your models here.

@admin.register(ChatUser)
class ChatUserAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'reply_required', 'continue_chat', 'auto_reply', 'last_msg_tym')
    date_hierarchy = 'last_msg_tym'
    search_fields = ('phone_number', )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('chat_user', 'seen_status', 'time_stamp', 'msg_type', 'order_pk', 'amount',)

    
    def order_pk(self, obj):
        if obj.order == None:
            return '-'
        else:
            return f"#{obj.order.pk}"
    
    def amount(self, obj):
        if obj.order == None:
            return "-"
        else:
            return f"₹ {obj.order.order_amount()}"