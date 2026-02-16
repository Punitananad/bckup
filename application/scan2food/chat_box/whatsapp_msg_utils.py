import requests
from .models import *
import json

from django.utils import timezone
from django.utils.timezone import localtime, make_aware

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from theatre.models import Order

####################################################
######   VARIABLES TO SEND THE WHATSAPP MESSAGE  ###
####################################################
ACCESS_TOKEN = "EAAJph1TVFooBQiftANmi38EQeqoiKdTgaXR4btXbYRaU6iAWAXyGkZAyMxPa9Ycx4LL8A6vu5W66bhaQqsFXbJnI0N1TjReL2dVN3zqH6ChAPRIz1oi0VdIC7eXjasq5VzNO53I2djJ8n99VYNkyOnhRu7RBuyQ3rvtW7fjMyUhzkbXPhFWJFFQXO0tIEPAZDZD"
PHONE_NUMBER_ID = "706345399217798"
VERIFY_TOKEN = "scan2food_my_token"

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}


# AUTO REPLY WHICH SEND TO CUSTOMER ON THERE FIRST MESSAGE
AUTO_REPLY = f"""*Hello!* 👋
Sit back, relax, and enjoy the movie 🍿🎬
Our team will connect you with a live agent shortly.

-- `team scan2food`
"""

# REFUND CONFIRMATION SEND TO CUSTOMER AFTER IT'S ORDER IS REFUNDED
REFUND_CONFIRMATION_TEMPLATE = """
Refund Confirmed!
✅ Your refund has been successfully processed.

💸 The amount will be credited to your original payment method within 5-7 working days. 

🏦 Thank you for your patience and for choosing Scan2Food. 

🙏 For any queries, feel free to contact us at support@scan2food.com 📧
— Team Scan2Food
"""

######################################################
########## ALL VARIABLES ENDS HERE.  #################
######################################################




##########################################################
#######   FUNCTION UPDATE THE CHAT-BOX WEBSOCKET     #####
##########################################################



##########################################################
################    ALL MESSAGE TEMPLATES ################
##########################################################
# AMOUNT MISSMATCH TEMPLATE
def amount_missmatch(phone_number, theatre_name, payout_amount, calculated_amount, difference):
    '''
    FUNCTION TO NOTIFY THE USER THAT YOUR'S ORDER IS SUCCESSFULLY REFUNDED
    AND YOU WILL GET YOUR REFUND  SOON WITH IN 5-7 WORKING DAYS.
    '''
    payload = {
    "messaging_product": "whatsapp",
    "to": phone_number,
    "type": "template",
    "template": {
        "name": "info",
        "language":
        {
            "code": "en"
        },
        "components": [
            {
                "type": "body",
                "parameters": [
                    { "type": "text", "text": theatre_name },
                    { "type": "text", "text": payout_amount },
                    { "type": "text", "text": calculated_amount },
                    { "type": "text", "text": difference}
                ]
            }
        ]
    }
    }

    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    requests.post(url=url, headers=HEADERS, json=payload)    

    return {"status" : "done"}



# CONFIRMATION TEMPLATE
def send_order_confirmation(phone_number, theatre_name, seat_name, order_pk):
    '''
    THIS FUNCTION SEND THE ORDER CONFIRMATION TEMPLATE TO THE CUSTOMER
    FOR THE FOOD ORDER
    '''
    ################################################
    # PAYLOAD FOR THE TEMPLATE WHICH IS REQUIRED ###
    ################################################
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
    # SEND THE WHATSAPP MESSAGE
    requests.post(url=url, headers=HEADERS, json=payload)
    # MESSAGE SUCCESSFULLY SENT



    # NOW SAVE THE MESSAGE
    save_message(
        phone_number=phone_number,
        msg_type="TEMPLATE",
        template="CONFIRMATION",
        order_id=order_pk
    )
    return {'status': 'success'}

# INVOICE TEMPLATE
def send_invoice(phone_number, order_pk):
    '''
    THIS FUNCTION SEND THE INVOICE TEMPLATE TO THE CUSTOMER
    FOR THE FOOD ORDER
    '''
    ################################################
    # PAYLOAD FOR THE TEMPLATE WHICH IS REQUIRED ###
    ################################################
    payload = {
    "messaging_product": "whatsapp",
    "to": phone_number,
    "type": "template",
    "template": {
        "name": "bill_invoice ",
        "language":
        {
            "code": "en"
        },
        "components": [
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
    # SEND THE WHATSAPP MESSAGE
    requests.post(url=url, headers=HEADERS, json=payload)
    # MESSAGE SUCCESSFULLY SENT



    # NOW SAVE THE MESSAGE
    save_message(
        phone_number=phone_number,
        msg_type="TEMPLATE",
        template="INVOICE",
        order_id=order_pk
        )

    return {'status': 'success'}


    
# REFUND CONFIRMATION TEMPLATE AFTER THE ORDER REFUND CONFIRMED AND SEND TO THE CUSTOMER
def send_refund_confirmation_message(phone_number):
    '''
    FUNCTION TO NOTIFY THE USER THAT YOUR'S ORDER IS SUCCESSFULLY REFUNDED
    AND YOU WILL GET YOUR REFUND  SOON WITH IN 5-7 WORKING DAYS.
    '''
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
    requests.post(url=url, headers=HEADERS, json=payload)

    user = ChatUser.objects.filter(phone_number=phone_number).first()
    if user == None:
        # create user
        user = ChatUser.objects.create(phone_number=phone_number)
    
    user.reply_required = False
    user.save()
    
    save_message(
        phone_number=phone_number,
        msg_type='TEMPLATE',
        template="REFUND",
        notify=True
        )
    return {'status': 'succes'}


# PARTIAL REFUND CONFIRMATION TEMPLATE AFTER THE ORDER REFUND CONFIRMED AND SEND TO THE CUSTOMER
def send_partial_refund_confirmation_message(phone_number, items, refund_amount):
    '''
    FUNCTION TO NOTIFY THE USER THAT YOUR'S ORDER IS SUCCESSFULLY REFUNDED
    AND YOU WILL GET YOUR REFUND  SOON WITH IN 5-7 WORKING DAYS.
    '''
    payload = {
    "messaging_product": "whatsapp",
    "to": phone_number,
    "type": "template",
    "template": {
        "name": "partial_refund",
        "language":
        {
            "code": "en"
        },
        "components": [
            {
                "type": "body",
                "parameters": [
                    { "type": "text", "text": items },
                    { "type": "text", "text": refund_amount },
                ]
            }
        ]
    }
    }

    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    requests.post(url=url, headers=HEADERS, json=payload)

    user = ChatUser.objects.filter(phone_number=phone_number).first()
    if user == None:
        # create user
        user = ChatUser.objects.create(phone_number=phone_number)
    
    user.reply_required = False
    user.save()
    
    save_message(
        phone_number=phone_number,
        msg_type='TEMPLATE',
        template="REFUND",
        notify=True
        )
    return {'status': 'succes'}


# REFUND QUERY SEND TO THEATRE STAFF TO ENTER THE REFUND OTP
def refund_query(phone_number, otp, order_pk):
    '''
    THIS FUNCTION SEND THE OTP TO THE THEATRE'S MANAGER FOR ANY ORDER REFUND
    AND ONLY THEN THE CUSTOMER GET THERE REFUND
    '''
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
    requests.post(url=url, headers=HEADERS, json=payload)
    
    return {'status': 'succes'}


# SEND NOTIFICATION TO THEATRE STAFF THAT YOUR'S QR SERVICES ARE ACTIVATED FORM NOW
def activate_qr_service(phone_number):
    '''
    FUNCTION NOTIFY THE THEATRE MANAGER THAT FROM NOW THE QR SERVICES ARE ACTIVATED AGAIN
    AND THEY WILL GET THE ORDER FROM SCAN2FOOD
    '''
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
    requests.post(url=url, headers=HEADERS, json=payload)
    
    return {'status': 'succes'}


# SEND NOTIFICATION TO THEATRE MANAGER SOMEBODY HAS DEACTIVATED THE QR SERVICE AND PRESS THE DEACTIVATE BUTTON
def deactivate_qr_service(phone_number):
    '''
    FUNCTION NOTIFY THE THEATRE MANAGER THAT FROM NOW THE QR SERVICES ARE DEACTIVATED
    AND THEY ARE NOT ABLE TO GET THE ORDER FROM SCAN2FOOD FROM NOW TILL THERE ACTIVATION
    '''
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
    requests.post(url=url, headers=HEADERS, json=payload)
    
    return {'status': 'succes'}


# RAISE REFUND REQUEST TEMPLATE AFTER THE RAISE REFUND REQUEST SEND TO THE CUSTOMER
def send_refund_raised_request(phone_number, order_id, refund_amount, theatre_name):
    '''
    FUNCTION TO NOTIFY THE USER THAT YOUR'S REFUND REQUEST IS INITIATED
    AND YOU WILL GET CALL FROM OUR TEAM SOON AFTER THE MOVIE OVER.
    '''
    payload = {
    "messaging_product": "whatsapp",
    "to": phone_number,
    "type": "template",
    "template": {
        "name": "refund_request",
        "language":
        {
            "code": "en"
        },
        "components": [
            {
                "type": "body",
                "parameters": [
                    { "type": "text", "text": order_id },
                    { "type": "text", "text": refund_amount },
                    { "type": "text", "text": theatre_name}
                ]
            }
        ]
    }
    }

    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    requests.post(url=url, headers=HEADERS, json=payload)

    user = ChatUser.objects.filter(phone_number=phone_number).first()
    if user == None:
        # create user
        user = ChatUser.objects.create(phone_number=phone_number)
    
    user.reply_required = False
    user.save()
    
    save_message(
        phone_number=phone_number,
        msg_type='TEMPLATE',
        template="REFUND",
        notify=True
        )
    return {'status': 'succes'}

#####################################################################
################### EVERY REPLY GOES FROM HERE ######################
#####################################################################

def reply_to_user(phone, text, reply_required=False):

    '''
    THIS FUNCTION WILL SEND THE MESSAGE TO THE USER WIHT PHONE NUMBER GIVEN
    '''
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": { "body": text }
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    
    user = ChatUser.objects.filter(phone_number=phone).first()
    user.auto_reply = False
    user.reply_required = reply_required
    user.continue_chat = True
    user.save()



######################################################################
#########  SAVE AND HANDLE INCOMMING MESSAGES ########################
######################################################################

def handle_incoming_message(data):
    '''
    IT WILL HANDLE THE INCOMMING MESSAGE FROM THE 
    '''

    sender_id = ""
    continue_chat = False
    reply_required = False
    auto_reply = True

    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            messages = value.get("messages")
            if messages:
                message = messages[0]
                sender_id = message["from"]

                text = message.get("text", {}).get("body", "")
                

                return_messaage = AUTO_REPLY
                user = ChatUser.objects.filter(phone_number=sender_id).first()

                if user == None:
                    user = ChatUser.objects.create(
                        phone_number=sender_id
                    )
                
                if user.continue_chat == False:
                    user.continue_chat = True

                    if user.auto_reply:
                        user.auto_reply = False
                        reply_to_user(sender_id, return_messaage, True)
                        user.reply_required = True
                
                user.save()
    
                save_message(phone_number=sender_id, context=text, notify=True)
    



def save_message(phone_number, context="", msg_type="INCOMING", template="", notify=False, order_id="", user_id=""):
    '''
    THIS CODE WILL ONLY SAVE THE WHATSAPP MESSAGE TEMPLATE IN THE DATABASE
    '''

    chat_user = ChatUser.objects.filter(
        phone_number=phone_number
    ).first()
    if chat_user == None:
        # CREATE THE NEW USER
        chat_user = ChatUser.objects.create(
            phone_number=phone_number,
        )
        chat_user.save()
    
    if order_id != "":
        order = Order.objects.get(pk=order_id)
        order.chatuser = chat_user
        order.save()

    # NOW SAVE THE MESSAGE
    message = Message.objects.create(
        chat_user=chat_user,
        context=context,
        msg_type=msg_type,
        template=template,
        order_id=order_id,
        user_id=user_id
    )

    message.save()

    if template == "CONFIRMATION":
        #  SAVE THE CHAT USER SO THAT IT DIDN'T SEE IN MESAGES
        chat_user.reply_required = False
        chat_user.continue_chat = False
        chat_user.auto_reply = True
        chat_user.save()
    
    if notify == True:
        update_websocket(phone_number=phone_number, msg_id=message.pk)


def update_websocket(phone_number, msg_id):
    message = Message.objects.get(pk=msg_id)
    chat_user = message.chat_user
    

    if message.msg_type == "INCOMING":
        chat_user.reply_required = True
    
    else:
        chat_user.reply_required = False

    # SAVE THE CHAT USER AND CACHE DATA
    chat_user.save()

    msg_data = message.json_data()
    msg_time = localtime(now()).strftime("%d-%b-%Y %I:%M %p")

    # JOSN DATA WHICH IS SENT TO THE USER INTERFACE USING THE WEBSOCKET TO ALL CONNECTED USERS
    theatre_detail = chat_user.last_theatre()
    json_data = {
        "pk": chat_user.pk,
        "phone_number": phone_number, # PHONE NUMBER FORM WHERE MSG COME OR WHERE HAVE TO SEND THE MESSAGE
        "msg_time": msg_time,
        "message_data": msg_data,
        'theatre_id': theatre_detail['theatre_id'],
        'theatre_name': theatre_detail['theatre_name'],
        'seat_id': theatre_detail['seat_id'],
        'seat_name': theatre_detail['seat_name'],
        'hall_name': theatre_detail['hall_name'],
    }
    
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'chat-consuer', # NAME OF GROUP WHERE WE HAVE TO SEND THE DATA
        {
            'type': 'brodcast_message', # FUNCTION WHICH SEND THE UPDATED DATA TO WEBSOCKET
            'message_data': json.dumps(
                json_data
            ) # DATA WHICH WE SENT TO THE WEBSOCKET
        }
    )

