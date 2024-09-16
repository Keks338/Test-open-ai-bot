import time

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import sync_to_async
import asyncio
import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import openai
from openai import OpenAI
from .models import BotUser
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TOKEN')

application = Application.builder().token(TOKEN).build()

# Сохранение "памяти" пользователя
# async def save_user_memory(user_id, memory_text):
#     # user_id уже является целым числом, так что передаем его напрямую
#     memory, created = await sync_to_async(UserMemory.objects.get_or_create)(user_id=user_id)
#     memory.memory = memory_text
#     await sync_to_async(memory.save)()


# Получение "памяти" пользователя
# async def get_user_memory(user_record, user):
#     try:
#         # Пытаемся получить или создать объект памяти пользователя
#         memory, created = await sync_to_async(UserMemory.objects.get_or_create)(user_id=user_record)
#         return memory.memory
#     except AttributeError:
#         # Если возникла ошибка AttributeError, пробуем найти пользователя
#         user_record = await sync_to_async(BotUser.objects.get)(user_id=user.id)
#         memory, created = await sync_to_async(UserMemory.objects.get_or_create)(user_id=user_record)
#         return ""
#     except UserMemory.DoesNotExist:
#         return ""


@csrf_exempt
async def webhook(request):
    if request.method == 'POST':
        # Логируем входящие обновления
        logger.info(f"Получено обновление: {request.body}")

        json_data = json.loads(request.body)
        update = Update.de_json(json_data, application.bot)
        # Используем await для добавления обновления в очередь
        await application.update_queue.put(update)
        return JsonResponse({"status": "ok"}, status=200)
    return JsonResponse({"status": "error"}, status=400)

# Функция для команды /start
async def start(update: Update, context):
    await update.message.reply_text("Привет! Я бот, с ИИ который может решать сложные математические решения.")

async def user_check(update, context):
    user = update.message.from_user
    bot_user, created = await sync_to_async(BotUser.objects.get_or_create)(user_id=user.id,
        defaults={
            'first_name': user.first_name,
            'last_name': user.last_name
        })
    if created == False:
        # bot_user, created = await sync_to_async(BotUser.objects.get_or_create)(user_id=user.id)
        # bot_user.thread_id = ""
        # await sync_to_async(bot_user.save)()
        await update.message.reply_text("Вы уже зарегистрированный пользователь")
    else:
        bot_user, created = await sync_to_async(BotUser.objects.get_or_create)(user_id=user.id)
        thread = client.beta.threads.create()
        print(thread.id)
        bot_user.thread_id = thread.id
        await sync_to_async(bot_user.save)()
        await update.message.reply_text("Вы не зарегистрированный пользователь, был, сейчас вы уже зарегистрированы.")

# Функция для обработки текстовых сообщений
async def handle_message(update: Update, context):
    text = update.message.text
    user = update.message.from_user
    user_record, created = await sync_to_async(BotUser.objects.get_or_create)(user_id=user.id)
    response = client.beta.threads.messages.create(
        thread_id=user_record.thread_id,
        role="user",
        content=text,
    )
    run = client.beta.threads.runs.create(
        thread_id=user_record.thread_id,
        assistant_id=os.getenv('Assistant_id'),
        instructions=f"User's name is {user_record.first_name}, and he has some problems in math. only you can help him."
    )
    while run.status != "completed":
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(
            thread_id=user_record.thread_id,
            run_id=run.id
        )
        print(run.status)

    messages = client.beta.threads.messages.list(
        thread_id=user_record.thread_id
    )



    # memory = await get_user_memory(user_record, user)
    # full_context = f"{memory} {text}"
    # full_context2 = f"{memory}\n Всё что выше написано, это история чата с этим пользователем, ниже то что сейчас отправил пользователь: {text}"
    # annotations = message_content.annotations
    # print(message_content)
    # bot_response = completion.choices[0].message.content

    # # Обновляем память пользователя
    # updated_memory = f"Вопрос пользователя: {full_context}\nОтвет ИИ: {bot_response}"
    # memory = await save_user_memory(user_record, updated_memory)
    await update.message.reply_text(f"{messages.data[0].content[0].text.value}")


# Добавляем обработчики команд и сообщений
application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('user_check', user_check))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
application.run_polling()