import requests
from .models import *
import datetime
import json

from django.utils import timezone
from django.utils.timezone import localtime

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

ACCESS_TOKEN = "EAAJph1TVFooBQiftANmi38EQeqoiKdTgaXR4btXbYRaU6iAWAXyGkZAyMxPa9Ycx4LL8A6vu5W66bhaQqsFXbJnI0N1TjReL2dVN3zqH6ChAPRIz1oi0VdIC7eXjasq5VzNO53I2djJ8n99VYNkyOnhRu7RBuyQ3rvtW7fjMyUhzkbXPhFWJFFQXO0tIEPAZDZD"
PHONE_NUMBER_ID = "706345399217798"
VERIFY_TOKEN = "scan2food_my_token"

def update_websocket(phone_number, message, msg_typ):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send) (
        'chat-consuer', # Group name where we send the data...
        {
            'type': 'update_message',  # function of ChatConsumer which send the data
            'updated_message': json.dumps({
                'phone_number': phone_number,
                'message': message,
                'msg_type': msg_typ,
                'msg_tym': localtime(timezone.now()).strftime("%I:%M %p"),
            })
        }
    )


headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def send_order_confirmation_message(phone_number, theatre_name, seat_name, order_pk):
    payload = {
    "messaging_product": "whatsapp",
    "to": phone_number,
    "type": "template",
    "template": {
        "name": "new_order_confirmation_",
        "language":
        {
            "code": "en"
        },
        "components": [
            {
                "type": "body",
                "parameters": [
                    { "type": "text", "text": theatre_name },
                    { "type": "text", "text": seat_name }
                ]
            },
            {
                "type": "button",
                "sub_type": "url",
                "index": "0",  # Refers to the first button in the template
                "parameters": [
                    { "type": "text", "text": f"{order_pk}" }  # dynamic URL
                ]
            }
        ]
    }
    }

    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    response = requests.post(url=url, headers=headers, json=payload)

    message = f"""
Thank you for your order, and welcome to {theatre_name} 🎬✨,

Your Seat: {seat_name}

Sit back, relax, and enjoy your movie without missing a single scene. We'll deliver your food and drinks to your seat shortly.

Enjoy the show! 🍿🎟️


url : https://scan2food.com/admin-portal/order-profile/{order_pk}

"""
    user = ChatUser.objects.filter(phone_number=phone_number).first()
    if user == None:
        # create user
        user = ChatUser.objects.create(phone_number=phone_number)
    
    user.first_reply_done = False
    user.save()
    
    save_message(phone_number=phone_number, message=message, msg_type='reply', notify=False)
    return {'status': 'succes'}

def send_refund_confirmation_message(phone_number):
    payload = {
    "messaging_product": "whatsapp",
    "to": phone_number,
    "type": "template",
    "template": {
        "name": "refund_confirmed ",
        "language":
        {
            "code": "en"
        }
    }
    }

    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    response = requests.post(url=url, headers=headers, json=payload)

    message = f"""
Refund Confirmed!
✅ Your refund has been successfully processed.

💸 The amount will be credited to your original payment method within 5-7 working days. 

🏦 Thank you for your patience and for choosing Scan2Food. 

🙏 For any queries, feel free to contact us at support@scan2food.com 📧
— Team Scan2Food
"""
    user = ChatUser.objects.filter(phone_number=phone_number).first()
    if user == None:
        # create user
        user = ChatUser.objects.create(phone_number=phone_number)
    
    user.first_reply_done = True
    user.save()
    
    save_message(phone_number=phone_number, message=message, msg_type='reply', notify=True)
    return {'status': 'succes'}

def refund_query(phone_number, otp, order_pk):
    payload = {
    "messaging_product": "whatsapp",
    "to": phone_number,
    "type": "template",
    "template": {
        "name": "refund_query",
        "language":
        {
            "code": "en_US"
        },
        "components": [
            {
                "type": "body",
                "parameters": [
                    { "type": "text", "text": otp },
                ]
            },
            {
                "type": "button",
                "sub_type": "url",
                "index": "0",  # Refers to the first button in the template
                "parameters": [
                    { "type": "text", "text": f"{order_pk}" }  # dynamic URL
                ]
            }
        ]
    }
    }

    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    response = requests.post(url=url, headers=headers, json=payload)
    
    return {'status': 'succes'}

def activate_qr_service(phone_number):
    payload = {
    "messaging_product": "whatsapp",
    "to": phone_number,
    "type": "template",
    "template": {
        "name": "activate_service",
        "language":
        {
            "code": "en"
        }
    }
    }

    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    response = requests.post(url=url, headers=headers, json=payload)
    
    return {'status': 'succes'}

def deactivate_qr_service(phone_number):
    payload = {
    "messaging_product": "whatsapp",
    "to": phone_number,
    "type": "template",
    "template": {
        "name": "deactivate_service",
        "language":
        {
            "code": "en"
        }
    }
    }

    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    response = requests.post(url=url, headers=headers, json=payload)
    
    return {'status': 'succes'}

# new code ........

# === Message Processing ===

temp_reply = f"""*Hello!* 👋
You've reached an automated number used by our system.
Please do not reply to this message — it's handled by a bot and not monitored for responses.

For support or inquiries, please contact us on Track Order url in Confirmation Message.
Thank you! 😊

-- `team scan2food`
"""

def handle_incoming_message(data):
    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            messages = value.get("messages")
            if messages:
                message = messages[0]
                sender_id = message["from"]
                text = message.get("text", {}).get("body", "")
                timestamp = message.get("timestamp")

                save_message(sender_id, text)

                return_messaage = temp_reply
                user = ChatUser.objects.filter(phone_number=sender_id).first()
                if user.first_reply_done == False:
                    reply_to_user(sender_id, return_messaage
                                )
                    user.first_reply_done = True
                    user.save()



def reply_to_user(phone, text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": { "body": text }
    }
    response = requests.post(url, headers=headers, json=payload)


def save_message(phone_number, message, msg_type="message", notify=True):
    user = ChatUser.objects.filter(phone_number=phone_number).first()
    if user == None:
        user = ChatUser.objects.create(phone_number=phone_number)
        user.save()

    # send over websocket
    if notify:
        update_websocket(phone_number=phone_number, message=message, msg_typ=msg_type)
    message = Message.objects.create(chat_user=user, content=message, msg_type=msg_type)
    message.save()
