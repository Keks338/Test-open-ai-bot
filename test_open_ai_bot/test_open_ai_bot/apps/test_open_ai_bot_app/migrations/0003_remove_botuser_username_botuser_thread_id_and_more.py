# Generated by Django 5.1.1 on 2024-09-14 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('test_open_ai_bot_app', '0002_usermemory'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='botuser',
            name='username',
        ),
        migrations.AddField(
            model_name='botuser',
            name='thread_id',
            field=models.TextField(default=''),
        ),
        migrations.DeleteModel(
            name='UserMemory',
        ),
    ]
