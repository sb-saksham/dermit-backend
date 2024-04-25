# Old test urls.py for django template test
from django.urls import path
from .views import index, room

app_name = "chat"

urlpatterns = [
    path('', index, name="chat_index"),
    path("<str:room_name>/", room, name="room"),
]
