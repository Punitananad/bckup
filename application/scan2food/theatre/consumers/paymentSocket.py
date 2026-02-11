import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from theatre.models import Order, Payment
import time
from django.conf import settings
from urllib.parse import parse_qs

class PaymentSocket(AsyncWebsocketConsumer):
    async def connect(self):
        # SECURITY: Check API key from query parameters
        query_string = self.scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        provided_key = query_params.get('key', [None])[0]
        
        # Verify the key
        if provided_key != settings.PAYMENT_STATUS_WS_KEY:
            # Invalid or missing key - reject connection
            await self.close()
            return
        
        # Key is valid - allow connection
        self.order_id = self.scope['url_route']['kwargs']['pk']
        # connect the websocket 
        # f"{self.order_id} is connected..."
        await self.accept()
    
    async def disconnect(self, code):
        await self.check_and_delete()

    @database_sync_to_async
    def check_and_delete(self):
        time.sleep(5)
        order = Order.objects.get(pk=self.order_id)
        payment = order.payment

        if payment.status != 'Success':
            # delete the payment
            # order.delete()
            # 'Order is deleted by the websocket...'
            pass