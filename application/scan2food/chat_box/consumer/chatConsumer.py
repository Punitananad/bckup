import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from django.utils.timezone import localtime

# IMPORTS FOR UPDATING SOMETHING IN DATABASE
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from chat_box.models import ChatUser, Message

# IMPORT OF WHATSAPP MSG UTILITIES
from chat_box.whatsapp_msg_utils import *


#############################################################################################
####################   FUNCTION SEND THE WHATSAPP MESSAGE  ##################################
#############################################################################################

# REPLY TO USER IS ALREADY THERE IN WHATSAPP MSG UTILS

class ChatConsumer(AsyncWebsocketConsumer):
    # FUNCTION RUN AT TIME OF NEW CONNECTION
    async def connect(self):
        self.group_name = 'chat-consuer'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    
    # FUNCTION RUN AT TIME OF DISCONNECTION
    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    async def receive(self, text_data=None):
        data = json.loads(text_data)

        task = data['task']
        
        if task == 'get-user-messages':
            # WANT TO UPDATE THE 
            # SEND THE LAST 10 MESSAGES OF THE USER OF PHONE NUMBER WHICH WAS GIVEN
            phone_number = data['phone_number']

            latest_messages = await self.get_messages(phone_number)


            # RETURN DATA 
            return_data = {
                'data-contains': 'phone-number-messages',
                'messages': latest_messages,
                'phone-number': phone_number
            }

            # SEND BACK DATA IN JSON
            await self.send(
                text_data=json.dumps(
                    return_data
                )
            )

    async def brodcast_message(self, event):
        # THIS FUNCTION ALREADY RUN AFTER THE CACHE UPDATE
        # GET THE MESSAGE DATA FROM THE EVENT
        message_data = json.loads(event['message_data'])
        # RETURN DATA 
        message_data['data-contains'] = 'new-outgoing-message'
        
        await self.send(
            text_data=json.dumps(
                message_data
            )
        )


    @database_sync_to_async
    def get_messages(self, phone_number):
        messages = (
            Message.objects.filter(chat_user__phone_number=phone_number)
            .order_by("-time_stamp")[:10]
        )

        return_data = []
        # RETURN ALL THE MESSAGES LDJFLKJALKFJDLKJFAJFD JFL;AJF L;
        for message in messages:
            return_data.append(message.json_data())
        return return_data

    