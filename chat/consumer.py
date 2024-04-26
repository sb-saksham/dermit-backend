import json
from uuid import UUID

from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from channels.generic.websocket import JsonWebsocketConsumer

from .api.serializers import MessageSerializer
from .models import Conversation, Message


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)


class ChatConsumer(JsonWebsocketConsumer):
    """
    This consumer is used to show user's online status,
    and send notifications.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_name = None

    def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            return
        self.room_name = "home"
        self.accept()
        self.send_json(
            {
                "type": "welcome_message",
                "message": "Hey there! You've successfully connected!",
            }
        )

    def disconnect(self, code):
        print("Disconnected!")
        return super().disconnect(code)

    def receive_json(self, content, **kwargs):
        message_type = content["type"]
        if message_type == "chat_message":
            message = Message.objects.create(
                from_user=self.user,
                content=content["message"],
                conversation=self.conversation,
            )
            # API CALL HERE/MODEL INFERENCE HERE

            # response = requests.post({
            #      "model": "gpt-3.5-turbo",
            #      "messages": [{"role": "user", "content": content["message"]}],
            #      "temperature": 0.7
            # }, {
            #   "Content-Type": "application/json",
            #   "Authorization: f"Bearer {OPENAI_API_KEY}"
            # })
            # message.response = response
            # message.save()

            async_to_sync(self.channel_layer.group_send)(
                self.conversation_name,
                {
                    "type": "chat_message_response",
                    "name": self.user.username,
                    "message": MessageSerializer(message).data,
                },
            )

        return super().receive_json(content, **kwargs)

    def chat_message_response(self, event):
        self.send_json(event)
