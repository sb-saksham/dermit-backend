from django.urls import path

from .consumer import ChatConsumer

websocket_urlpatterns = [
    path("chats/<conversation_id>/", ChatConsumer.as_asgi()),
]
