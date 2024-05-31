from django.contrib.auth import get_user_model
from rest_framework import serializers
from chat.models import Message, Conversation, Image


User = get_user_model()


class LastMessageSerializer(serializers.Serializer):
    user = serializers.CharField(read_only=True)
    ai = serializers.CharField(read_only=True)
    
    class Meta:
        fields=("user", "ai")

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email"]


class MessageSerializer(serializers.ModelSerializer):
    from_user = serializers.SerializerMethodField()
    conversation = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = (
            "id",
            "conversation",
            "from_user",
            "content",
            "timestamp",
            "is_response",
        )

    def get_conversation(self, obj):
        return str(obj.conversation.id)

    def get_from_user(self, obj):
        return UserSerializer(obj.from_user).data


class ConversationSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    # user = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ("id", "name", "last_message", "user")

    def get_last_message(self, obj):
        messages = obj.messages.all().order_by("-timestamp")
        if not messages.exists():
            return None
        last_msg = {
            "user": messages[1].content,
            "ai": messages[0].content,
        }
        
        return LastMessageSerializer(last_msg).data

    # def get_user(self, obj):
    #     if obj.messages.first():
    #         user = obj.messages.first().from_user
    #         return UserSerializer(user).data
    #     return
        
            
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ("id", "user", "name", "image", "size")