import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from theatre.models import Order, Payment
import time

class PaymentSocket(AsyncWebsocketConsumer):
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['pk']
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