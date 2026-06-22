from django.urls import path

from .consumers import TicketConsumer


# Rutas exclusivas de WebSocket.
websocket_urlpatterns = [
    path('ws/tickets/', TicketConsumer.as_asgi()),
]