# Generated by Django 5.1.1 on 2024-10-03 08:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('test_open_ai_bot_app', '0002_botuser_chat_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='botuser',
            name='chat_id',
        ),
    ]
