import time

from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import sync_to_async
import asyncio
import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import openai
from openai import OpenAI
from .models import BotUser
from dotenv import load_dotenv
from .tasks import *
import os

load_dotenv()

client = OpenAI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TOKEN')

application = Application.builder().token(TOKEN).build()


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

async def operator_def(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    user_record = await sync_to_async(BotUser.objects.get)(user_id = user.id)
    user_record2 = await sync_to_async(BotUser.objects.get)(user_id = int(os.getenv('Operator_User_id')))
    if user_record2.operator_id == 0:
        user_record2.operator_id = user_record.user_id
        await sync_to_async(user_record2.save)()
    user_record3 = await sync_to_async(BotUser.objects.get)(user_id = user_record2.operator_id)
    user1_id = int(os.getenv('Operator_User_id'))

    if user_record.is_operator:
        print("Я оператор")
        if "stopitnow" in text:
            user_record3.needed_operator = 0
            user_record2.needed_operator = 0
            user_record2.operator_id = 0
            await sync_to_async(user_record3.save)()
            await sync_to_async(user_record2.save)()
            return
        await context.bot.send_message(chat_id=user_record2.operator_id, text=update.message.text)
    else:
        await context.bot.send_message(chat_id=user1_id, text=update.message.text)


async def plot_graph(equation_str: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    import numpy as np
    import matplotlib.pyplot as plt

    params = json.loads(equation_str)
    equation = params.get("equation_str")

    print(equation)
    if "sin" in equation:
        x = np.linspace(-2 * np.pi, 2 * np.pi, 400)
    elif "cos" in equation:
        x = np.linspace(-2 * np.pi, 2 * np.pi, 400)
    else:
        x = np.linspace(-10, 10, 400)
    equation_str = equation.replace('^', '**')
    equation_str = equation_str.replace('sin', 'np.sin')
    equation_str = equation_str.replace('cos', 'np.cos')
    try:
        y = eval(equation_str.split('=')[1].strip())

        plt.plot(x, y)
        plt.title(f'График для уравнения: {equation_str}')
        plt.xlabel('x')
        plt.ylabel('y')
        plt.grid(True)
        plt.savefig('plot.png')
        plt.clf()
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('plot.png', 'rb'))
    except Exception as e:
        print(f"Ошибка при построении графика: {e}")
        return f"Error while plotting the graph: {e}"
    return "Function completed succesfully! the image of function was sent to user!"




# Функция для команды /start
async def start(update: Update, context):
    await update.message.reply_text("Привет! Я бот, с ИИ который может решать сложные математические решения. Давайте начнём с регистрации вас, впишите /user_check и сами все узнаете!")

async def user_check(update, context):
    user = update.message.from_user
    bot_user, created = await sync_to_async(BotUser.objects.get_or_create)(user_id=user.id,
        defaults={
            'first_name': user.first_name,
            'last_name': user.last_name
        })
    if created == False:
        await update.message.reply_text("Вы уже зарегистрированный пользователь")
    else:
        update_asst_db.delay()
        user_record = await sync_to_async(BotUser.objects.get)(user_id=user.id)
        thread = client.beta.threads.create()
        print(thread.id)
        user_record.thread_id = thread.id
        await sync_to_async(user_record.save)()
        await update.message.reply_text("Вы не зарегистрированный пользователь, был, сейчас вы уже зарегистрированы.")

# Функция для обработки текстовых сообщений
async def handle_message(update: Update, context):
    text = update.message.text
    user = update.message.from_user
    current_time = timezone.now()
    try:
        user_record = await sync_to_async(BotUser.objects.get)(user_id=user.id)
    except BotUser.DoesNotExist:
        await update.message.reply_text("Вы не зарегистрированы, используйте /user_check чтобы зарегистрироваться")
        return print("User Does Not Registered")
    user_record2 = await sync_to_async(BotUser.objects.get)(user_id=int(os.getenv('Operator_User_id')))
    if user_record.needed_operator:
        await operator_def(update, context)
    else:
        if user_record.thread_id == "":
            update_asst_db.delay()
            thread = client.beta.threads.create()
            print(thread.id)
            user_record.thread_id = thread.id
            await sync_to_async(user_record.save)()

        time_difference = current_time - user_record.date_thread_created
        diff_hours = time_difference.total_seconds()/3600

        if diff_hours > 24:
            remove_thread.delay(user_record.thread_id)
            await update.message.reply_text("С момента создания потока прошло 24 часа, память сообщений очищена.")

        if user_record.thread_id == "":
            update_asst_db.delay()
            thread = client.beta.threads.create()
            print(thread.id)
            user_record.thread_id = thread.id
            await sync_to_async(user_record.save)()

        response = client.beta.threads.messages.create(
            thread_id=user_record.thread_id,
            role="user",
            content=text,
        )
        run = client.beta.threads.runs.create(
            thread_id=user_record.thread_id,
            assistant_id=os.getenv('Assistant_id'),
            instructions=f"User's name is {user_record.first_name}, and he has some problems in math. only you can help him. You can only use the .docx file which given to you."
        )
        while run.status != "completed":
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=user_record.thread_id,
                run_id=run.id
            )
            print(run.status)
            if run.status == "incomplete":
                user_record.needed_operator = 1
                user_record2.needed_operator = 1
                await sync_to_async(user_record.save)()
                await sync_to_async(user_record2.save)()
                remove_thread.delay(user_record.thread_id)
                await operator_def(update, context)
                return print("AsstCanNotAnswer")
            elif run.status == "requires_action":
                function_res = await plot_graph(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments, update, context)
                client.beta.threads.runs.submit_tool_outputs(
                    thread_id=user_record.thread_id,
                    run_id=run.id,
                    tool_outputs=[
                        {
                            "tool_call_id": run.required_action.submit_tool_outputs.tool_calls[0].id,
                            "output": function_res
                        }
                    ]
                )

        messages = client.beta.threads.messages.list(
            thread_id=user_record.thread_id
        )
        await update.message.reply_text(f"{messages.data[0].content[0].text.value}")


# Добавляем обработчики команд и сообщений
application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('user_check', user_check))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))