from django.core.management.base import BaseCommand
from telegram.ext import Application

# Инициализация вашего бота
from ...views import application  # Импортируйте объект бота

class Command(BaseCommand):
    help = 'Запускает Telegram-бота'

    def handle(self, *args, **kwargs):
        # Запуск бота
        application.run_polling()
