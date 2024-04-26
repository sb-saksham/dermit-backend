from django.urls import re_path

from .consumer import ChatConsumer

websocket_urlpatterns = [
    path("<conversation_name>/", ChatConsumer.as_asgi()),
]