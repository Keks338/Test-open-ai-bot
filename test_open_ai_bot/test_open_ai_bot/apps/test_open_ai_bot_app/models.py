from django.db import models
from django.contrib.auth.models import User

class BotUser(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    date_thread_created = models.DateTimeField(auto_now=True)
    thread_id = models.TextField(default="")
    operator_id = models.IntegerField(default=0)
    needed_operator = models.BooleanField(default=False)
    is_operator = models.BooleanField(default=False)