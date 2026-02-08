from django.db import models
from django.utils.timezone import localtime, now

# IMPORT FOR THE USER WHO IS MESSAGING
from django.contrib.auth.models import User


# Create your models here.
class ChatUser(models.Model):
    phone_number = models.CharField(
        max_length=15, unique=True, db_index=True, null=False, blank=False
    )
    
    reply_required = models.BooleanField(
        default=False
    )
    
    continue_chat = models.BooleanField(
        default=False
    )
    # THIS TABLE CONNECTED WITH THEATRE ORDER
    # USER.ORDERS
    auto_reply = models.BooleanField(
        default=True
    )

    last_msg_tym = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.phone_number
    
    def last_theatre(self):
        try:
            last_order = self.order_set.last()
            theatre = last_order.seat.row.hall.theatre
            return_data = {
                'theatre_id': theatre.pk,
                'theatre_name': theatre.name,
                'seat_id': last_order.seat.pk,
                'seat_name': last_order.seat.name,
                'hall_name': last_order.seat.row.hall.name,
            }
        
        except Exception as e:
            return_data = {
                'theatre_id': "",
                'theatre_name': "",
                'seat_id': "",
                'seat_name': "",
                'hall_name': "",
            }
            
        return return_data

class Message(models.Model):
    # MSG TYPE WHETHER THE MESSAGE IS REPLY OR NORMAL MESSAGE
    MSG_TYPE = [
        ('INCOMING', 'INCOMING'),
        ('OUTGOING', 'OUTGOING'),
        ('TEMPLATE', 'TEMPLATE')
    ]

    # TEMPLATE NAME
    # SHOW THE MESSAGE ACCORDING TO THE TEMPLATE NOT TO SAVE THE ENTIRE MESSAGE OF ORDER
    TEMPLATE_NAME = [
        ('CONFIRMATION', 'CONFIRMATION'),
        ('REFUND', 'REFUND'),
    ]

    chat_user = models.ForeignKey(
        ChatUser, on_delete=models.CASCADE
    )
    
    context = models.TextField()
    seen_status = models.BooleanField(
        default=False
    )
    
    time_stamp=models.DateTimeField(
        auto_now_add=True
    )

    msg_type = models.CharField(
        max_length=10,
        choices=MSG_TYPE
    )

    template = models.CharField(
        max_length=15,
        choices=TEMPLATE_NAME,
        default="",
        null=True,
        blank=True
    )

    order = models.ForeignKey(
        'theatre.order',
        on_delete=models.SET_NULL,
        default="",
        null=True,
        blank=True
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        default=""
    )

    def save(self, *args, **kwargs):
        # Save message first
        super().save(*args, **kwargs)

        # Update chat_user.last_msg_tym
        if self.chat_user:
            self.chat_user.last_msg_tym = self.time_stamp
            self.chat_user.save(update_fields=["last_msg_tym"])


    def __str__(self):
        return f"{self.msg_type}-{self.pk}"
    
    def json_data (self):
        localized_time = localtime(self.time_stamp)
        msg_time = localized_time.strftime("%d-%b-%Y %I:%M %p")
        seat_name = ""
        hall_name = ""
        theatre_name = ""
        theatre_id = ""
        img_url = ""
        
        if self.msg_type == "OUTGOING":
            try:
                img_url = self.user.userprofile.theatre.detail.logo.url
            except:
                img_url = "/static/assets/images/brand/favicon.png"
        try:
            order_id = self.order.id
            seat_name = self.order.seat.name
            hall_name = self.order.seat.row.hall.name
            theatre_id = self.order.seat.row.hall.theatre.id
            theatre_name = self.order.seat.row.hall.theatre.name
        except: 
            order_id = ""
        
        try:
            user = self.user.first_name

        except:
            user = ""

        return_data = {
            "user_id" : self.chat_user.id,
            "context" : self.context,
            "seen_status": self.seen_status,
            "msg_time": msg_time,
            'msg_type': self.msg_type,
            "template": self.template,
            "order_id": order_id,
            "user": user,
            "seat_name": seat_name,
            "hall_name": hall_name,
            "theatre_name": theatre_name,
            "thetre_id": theatre_id,
            "img_url": img_url
        }

        return return_data