from django.db import models

# Create your models here.
import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    user = models.ForeignKey(to=User, blank=True, on_delete=models.CASCADE)

    def join(self, user):
        self.user = user
        self.save()

    def __str__(self):
        return f"{self.name} ({self.get_online_count()})"


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="messages_from_me"
    )
    content = models.CharField(max_length=512)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.from_user.username} : {self.content} [{self.timestamp}]"
