"""
ASGI config for theatreApp project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'theatreApp.settings')

django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import URLRouter, ProtocolTypeRouter
from channels.auth import AuthMiddlewareStack

from theatre.routing import urlpatterns as theatre_url
from chat_box.routing import urlpatternss as chat_urls

urlpatterns = theatre_url + chat_urls

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            urlpatterns
        )
    )
})