from django.urls import path
from . import views

app_name = "chat_box"

urlpatterns = [
    path('webhook', views.webhook, name='webhook'),
    path('chat-users', views.get_chat_users, name='chat-users'),
    path('get-user-messages', views.get_user_messages, name="get-user-messages"),
    path('send-whatsapp-message', views.send_whatsapp_message, name='send-whatsapp-message'),
    path('get-chat-from-order-id/<int:pk>', views.get_chats_from_order_id, name='get-chat-from-order-id'),

    path('', views.index, name='index'),
]
