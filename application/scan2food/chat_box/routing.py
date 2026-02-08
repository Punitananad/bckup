from django.urls import path

from .consumer.chatConsumer import ChatConsumer

urlpatternss = [
    path('ws/chat-socket/', ChatConsumer.as_asgi())
]