import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from theatre.models import Order, Payment
import time

class PaymentSocket(AsyncWebsocketConsumer):
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['pk']
        
        # SECURITY: Validate that order exists before allowing connection
        order_exists = await self.check_order_exists()
        
        if not order_exists:
            # Order doesn't exist - reject connection
            await self.close()
            return
        
        # Order exists - allow connection
        await self.accept()
    
    @database_sync_to_async
    def check_order_exists(self):
        """Check if the order exists in database"""
        try:
            Order.objects.get(pk=self.order_id)
            return True
        except Order.DoesNotExist:
            return False
    
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