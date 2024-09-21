from django.db import models

class BotUser(models.Model):
    user_id = models.IntegerField(unique=True)
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    date_thread_created = models.DateTimeField(auto_now=True)
    thread_id = models.TextField(default="")