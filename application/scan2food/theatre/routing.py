from django.urls import path

from .consumers.allSeatConsumer import AllSeatConsumers
from .consumers.paymentSocket import PaymentSocket

urlpatterns = [
    path('ws/all-seat-datasocket/', AllSeatConsumers.as_asgi()),
    path('ws/payment-socket/<int:pk>/', PaymentSocket.as_asgi()),
]