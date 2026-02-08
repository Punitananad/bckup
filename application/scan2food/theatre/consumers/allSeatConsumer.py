import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.cache import cache
from django.utils.timezone import localtime
from django.utils import timezone

global connected_theatres
connected_theatres = []

class AllSeatConsumers(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "all-seat-status"
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()
    
    async def disconnect(self, code):
        theatre_id = getattr(self, 'theatre_id', None)
        
        try:
            if theatre_id != None:
                connected_theatres.remove(theatre_id)
                if theatre_id in connected_theatres:
                    pass
                else:
                    updated_table_data = {'disconnected_theatre_id': theatre_id, 'msg_typ': 'disconnected_theatre'}
                    await self.channel_layer.group_send(
                        "all-seat-status",
                        {
                            'type': 'table_data',
                            'updated_table_data': json.dumps(updated_table_data)
                        }
                    )
        except:
            pass

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def table_data(self, event):
        updated_table_data = event['updated_table_data']

        data = json.loads(updated_table_data)
        msg_typ = data['msg_typ']

        try:
            if msg_typ == "order_seen":
                seat_id = data['seat_id']
                seat_id = f"seat-id-{seat_id}"

                live_orders = cache.get('live-orders')
                
                if live_orders:
                    seat_data = live_orders[seat_id]
                    if seat_data:

                        if live_orders[seat_id]['is_shown'] == False:

                            live_orders[seat_id]['is_shown'] = True
                            cache.set('live-orders', live_orders, timeout=60*5)
                        else:
                            pass
                    else:
                        cache.delete('live-order')


            elif msg_typ == "confirmation":
                # add the order in seat_id
                seat_id = data['seat_id']
                seat_id = f"seat-id-{seat_id}"
                
                seat = data['seat_name']
                seat_name = seat.split(" | ")[1]
                hall_name = seat.split(" | ")[0]
                live_orders = cache.get('live-orders')

                if live_orders:
                    seat_data = {
                        'seat_id': data['seat_id'],
                        'seat_name': seat_name,
                        'hall_name': hall_name,
                        'is_vacent': False,
                        'theatre_id': data['theatre_id'],
                        'theatre_name': data['theatre_name'],
                        'payment_method': data['payment_method'],
                        'payment_status': data['payment_status'],
                        'is_shown': False,
                        'payment_time': localtime(timezone.now()).strftime("%d-%b-%Y|%I:%M %p"),
                        'amount': data['amount'],
                        'order_id': data['order_id'],
                        'max_time': data['max_time'],
                    }
                    live_orders[seat_id] = seat_data
                    cache.set('live-orders', live_orders, timeout=60 * 5)  # Cache for 5 minutes (300 sec)


            elif msg_typ == "Delivered":
                seat_id = data['seat_id']
                seat_id = f"seat-id-{seat_id}"

                live_orders = cache.get('live-orders')

                if live_orders:
                    # delete the seat_id
                    del live_orders[seat_id]
                    # update the cache data
                    cache.set('live-orders', live_orders, timeout=60 * 5)  # Cache for 5 minutes (300 sec)
                    
            elif msg_typ == 'refund-conformmation':
                seat_id = data['seat_id']
                seat_id = f"seat-id-{seat_id}"

                live_orders = cache.get('live-orders')

                if live_orders:
                    # delete the seat_id
                    del live_orders[seat_id]
                    # update the cache data
                    cache.set('live-orders', live_orders, timeout=60 * 5)  # Cache for 5 minutes (300 sec)

            elif msg_typ == 'Cancelation':
                seat_id = data['seat_id']
                seat_id = f"seat-id-{seat_id}"

                live_orders = cache.get('live-orders')

                if live_orders:
                    # delete the seat_id
                    del live_orders[seat_id]
                    # update the cache data
                    cache.set('live-orders', live_orders, timeout=60 * 5)  # Cache for 5 minutes (300 sec)
                    
                
        except:
            pass

        await self.send(
            text_data=json.dumps(
                {
                    'updated_table_data': updated_table_data
                }
            )
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        theatre_id = text_data_json['theatre_id']

        if theatre_id == 'admin':
            updated_table_data = json.dumps(
                {'msg_typ': 'all-connected-theatres', "connected_theatres": connected_theatres}
            )
            await self.send(
                text_data=json.dumps(
                    {'updated_table_data': updated_table_data}
                )
            )
        else:
            self.theatre_id = theatre_id
            connected_theatres.append(theatre_id)
            updated_table_data = {'connected_theatre_id': theatre_id, 'msg_typ': 'connected_theatre'}

            await self.channel_layer.group_send(
                "all-seat-status",
                {
                    'type': 'table_data',
                    'updated_table_data': json.dumps(updated_table_data)
                }
            )