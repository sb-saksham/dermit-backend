import json
from uuid import UUID

from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from channels.generic.websocket import JsonWebsocketConsumer

from .api.serializers import MessageSerializer
from .models import Conversation, Message
from .rag_model import RAG
from langchain.memory import ConversationBufferMemory


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)


class ChatConsumer(JsonWebsocketConsumer):
    """
    This consumer is used to relay chat messages and its response
    """

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.conversation_id = None
        self.conversation = None

    def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            return
        self.accept()
        self.conversation_id = f"{self.scope['url_route']['kwargs']['conversation_id']}"
        self.conversation, created = Conversation.objects.get_or_create(
            id=self.conversation_id,
        )
        async_to_sync(self.channel_layer.group_add)(
            self.conversation_id,
            self.channel_name,
        )
        self.send_json(
            {
                "type": "welcome_message",
                "message": "Hey there! You've successfully connected!",
            }
        )
        self.rag = RAG()
        self.memory = ConversationBufferMemory(memory_key="chat_history")

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
            async_to_sync(self.channel_layer.group_send)(
                self.conversation_id,
                {
                    "type": "chat_message_echo",
                    "name": self.user.username,
                    "message": MessageSerializer(message).data,
                },
            )
            # API CALL HERE/MODEL INFERENCE HERE

            incoming_message = message.content

            query = incoming_message

            agent_exe = self.rag.agent_executor.invoke(
                {"input": query, "chat_history": self.memory.chat_memory.messages},
                config={"configurable": {"session_id": "<foo>"}},
            )
            rag_response = agent_exe.get("output")
            print("rag res: ")
            print(rag_response)

            self.rag.manage_memory(
                memory=self.memory, query=query, response=rag_response
            )
            print("memory: ", self.memory)

            res_message = Message.objects.create(
                from_user=self.user,
                content=rag_response,
                conversation=self.conversation,
                is_response=True,
            )
            async_to_sync(self.channel_layer.group_send)(
                self.conversation_id,
                {
                    "type": "chat_message_echo",
                    "name": self.user.username,
                    "message": MessageSerializer(res_message).data,
                },
            )
        return super().receive_json(content, **kwargs)

    def chat_message_echo(self, event):
        self.send_json(event)
