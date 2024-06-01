import uuid
import os
from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings

User = get_user_model()


class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    user = models.ForeignKey(to=User, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id}"


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="messages_from_me"
    )
    content = models.TextField(max_length=512)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_response = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.from_user.username} : {self.content} [{self.timestamp}]"

class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="images")
    ## chat = testing without chatting id, will add later on
    name = models.CharField(max_length=256)
    size = models.BigIntegerField()
    image = models.ImageField(default="")
    
    def __str__(self):
        return f"Image {self.id} - {self.name}"
    