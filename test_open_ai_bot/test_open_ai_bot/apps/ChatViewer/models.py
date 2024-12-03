from django.db import models
from ..test_open_ai_bot_app.models import BotUser


class ChatViewer(models.Model):
    chat_id = models.ForeignKey(BotUser, on_delete=models.CASCADE)
    sender = models.CharField(default="", max_length=255)
    sender_type = models.CharField(default="", max_length=255)
    Message_Creation_Date = models.DateTimeField(auto_now_add=True)
    message = models.TextField(default="")
    type = models.CharField(default="", max_length=255)
