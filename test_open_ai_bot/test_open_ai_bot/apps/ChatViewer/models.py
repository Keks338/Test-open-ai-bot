from django.db import models
from ..test_open_ai_bot_app.models import BotUser


class ChatViewer(models.Model):
    chat_id = models.ForeignKey(BotUser, on_delete=models.CASCADE)
    sender = models.CharField(max_length=255)
    sender_type = models.CharField(max_length=255)
    message = models.TextField(default="")

