from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from chat_box.whatsapp_msg_utils import *


def send_whatsapp_template(phone_number="", msg_typ="", seat_name="", theatre_name="", order_id="", otp="", items="", refund_amount=""):
    msg_type = msg_typ
    if msg_type == 'confirmation':
        theatre_name = theatre_name
        seat_name = seat_name
        order_pk = order_id
        send_order_confirmation(
            phone_number=phone_number,
            theatre_name=theatre_name,
            seat_name=seat_name,
            order_pk=order_pk
            )


    ############## PENDING
    elif msg_type == 'reply':
        message = message
        reply_to_user(phone=phone_number, text=message)


    ############   PENDING
    elif msg_type == 'refund-conformation':
        send_refund_confirmation_message(phone_number=phone_number)
    
    # partial-refund-conformation
    elif msg_type == "partial-refund-conformation":
        send_partial_refund_confirmation_message(phone_number=phone_number, items=items, refund_amount=refund_amount)

    ###########   PENDING
    elif msg_type == 'refund_query':
        order_pk = order_id
        otp = otp

        refund_query(phone_number=phone_number, otp=otp, order_pk=order_pk)
    

    ############  PENDING
    elif msg_type == "activate-qr-service":
        activate_qr_service(phone_number=phone_number)
    
    ########### PENDING
    elif msg_type == "deactivate-qr-service":
        deactivate_qr_service(phone_number=phone_number)

    elif msg_type == "raise-refund-request":
        send_refund_raised_request(phone_number=phone_number, refund_amount=refund_amount, theatre_name=theatre_name, order_id=order_id)

    return True


def update_websocket(theatre_id="", seat_id="", is_vacent="", payment_panding="", theatre_name="", seat_name="", bg_type="bg-success", message="", customer_phone="", customer_message="", notification_numbers="", group="", msg_typ = "", order_id="", amount="", payment_method="", payment_status="", max_time=30):
    '''This function will send the data to the websocket by just calling this function'''
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send) (
        'all-seat-status', # Group Name we want to send the updated data
        {
            'type': 'table_data', # function which send the data to webcocket, predefined in AllSeatConsumer.py file.
            'updated_table_data': json.dumps(
                {
                    'theatre_id': theatre_id,
                    "seat_id": seat_id,
                    "is_vacent": is_vacent,
                    "payment_panding": payment_panding,
                    'seat_name': seat_name,
                    'theatre_name': theatre_name,
                    'order_id': order_id,
                    'type': bg_type,
                    'message': message,
                    'customer-phone': customer_phone,
                    'customer-message': customer_message,
                    'notification_numbers': notification_numbers,
                    "group": group,
                    "amount": amount,
                    'msg_typ': msg_typ,
                    'payment_method': payment_method,
                    'payment_status': payment_status,
                    'max_time': max_time,
                } # Data which we want to send to the webcocker
            )
        }
    )

    if msg_typ == 'confirmation':
        phone_number = ""
        if "+91" in customer_phone:
            phone_number = customer_phone.replace("+", "")
        else:
            phone_number = f"91{customer_phone}"
        
        # send whatsapp message
        send_whatsapp_template(phone_number=phone_number, msg_typ=msg_typ, seat_name=seat_name, theatre_name=theatre_name, order_id=order_id)


    elif msg_typ == 'generate-otp':
        phone_number = ""
        if "+91" in customer_phone:
            phone_number = customer_phone.replace("+", "")
        else:
            phone_number = f"91{customer_phone}"
  
        # send whatsapp template
        send_whatsapp_template(phone_number=phone_number,otp=customer_message, order_id=order_id, msg_typ='refund_query')
    
    elif msg_typ == 'scaning-service-status':
        phone_number = ""
        if "+91" in customer_phone:
            phone_number = customer_phone.replace("+", "")
        else:
            phone_number = f"91{customer_phone}"
        
        # send whatsapp template
        qr_status = customer_message
        if qr_status == 'Activated':
            send_whatsapp_template(phone_number=phone_number, msg_typ='activate-qr-service')
        elif qr_status == 'Deactivated':
            send_whatsapp_template(phone_number=phone_number, msg_typ='deactivate-qr-service')
