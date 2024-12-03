import time

from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import sync_to_async
import asyncio
import json
import logging
import openai
from openai import OpenAI
from .models import BotUser
from ..ChatViewer.models import ChatViewer
from dotenv import load_dotenv
from .tasks import *
import os

load_dotenv()

client = OpenAI()

# def operator_def():
#     user = str("user_id")
#     text = str("User_text")
#     photos = str("user_photo")
#     user_record = BotUser.objects.get(user_id = user)
#     user_record2 = BotUser.objects.get(user_id = int(os.getenv('Operator_User_id')))
#     if user_record2.operator_id == 0:
#         user_record2.operator_id = user_record.user_id
#         user_record2.save()
#     user_record3 = BotUser.objects.get(user_id = user_record2.operator_id)
#     user1_id = int(os.getenv('Operator_User_id'))
#
#     if user_record.is_operator:
#         print("Я оператор")
#         if photos:
#             highest_resolution_photo = photos[-1]
#             ChatViewer.objects.create(chat_id=user_record3, sender="Оператор", sender_type="Operator", message="<Отправлено Изображение>")
#             # context.bot.send_photo(chat_id=user_record2.operator_id, photo=highest_resolution_photo)
#         if "stopitnow" in text:
#             user_record3.needed_operator = 0
#             user_record2.needed_operator = 0
#             user_record2.operator_id = 0
#             user_record3.save()
#             user_record2.save()
#             return
#         # ChatViewer.objects.create(chat_id=user_record3, sender="Оператор", sender_type="Operator", message=update.message.text)
#         # context.bot.send_message(chat_id=user_record2.operator_id, text=update.message.text)
#     else:
#         print("kok")
#         # ChatViewer.objects.acreate(chat_id=user_record3, sender=user_record3.first_name, sender_type="User", message=update.message.text)
#         # context.bot.send_message(chat_id=user1_id, text=update.message.text)


def plot_graph(equation_str: str):
    import numpy as np
    import matplotlib.pyplot as plt

    params = json.loads(equation_str)
    equation = params.get("equation_str")
    user = str("User_id")
    user_record = BotUser.objects.get(user_id=user.id)
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
        # context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('plot.png', 'rb'))
        ChatViewer.objects.create(chat_id=user_record, sender="ChatGPT", sender_type="User", message="<Отправлено Изображение>")
    except Exception as e:
        print(f"Ошибка при построении графика: {e}")
        return f"Error while plotting the graph: {e}"
    return "Function completed succesfully! the image of function was sent to user!"





# Функция для обработки текстовых сообщений
@csrf_exempt
def send_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        Incomplete_word_massa = ["Извините", "К сожалению"]
        text = data["text"]
        user = request.user
        current_time = timezone.now()
        try:
            user_record = BotUser.objects.get(user_id=user)
        except BotUser.DoesNotExist:
            ChatViewer.objects.create(chat_id=user_record, sender="ChatGPT", sender_type="User",message="Вы не зарегистрированы, используйте /user_check чтобы зарегистрироваться")
            return print("User Does Not Registered")
        try:
            user_record2 = BotUser.objects.get(is_operator=True)
        except BotUser.DoesNotExist:
            print("WARNING!!! Operator role doesn't found in any of users!")

        if user_record.needed_operator:
            print("ll")
            # operator_def(update, context)
        else:
            if user_record.thread_id == "":
                update_asst_db.delay()
                thread = client.beta.threads.create()
                print(thread.id)
                user_record.thread_id = thread.id
                user_record.save()

            time_difference = current_time - user_record.date_thread_created
            diff_hours = time_difference.total_seconds()/3600

            if diff_hours > 24:
                remove_thread.delay(user_record.thread_id)
                ChatViewer.objects.create(chat_id=user_record, sender="ChatGPT", sender_type="User",message="С момента создания потока прошло 24 часа, память сообщений очищена.")

            if user_record.thread_id == "":
                update_asst_db.delay()
                thread = client.beta.threads.create()
                print(thread.id)
                user_record.thread_id = thread.id
                user_record.save()

            response = client.beta.threads.messages.create(
                thread_id=user_record.thread_id,
                role="user",
                content=text,
            )
            run = client.beta.threads.runs.create(
                thread_id=user_record.thread_id,
                assistant_id=os.getenv('Assistant_id'),
                instructions=f"User's name is {user.first_name}, or user's username -> {user.username}, and he has some problems in math. only you can help him. You can only use the .docx file which given to you."
            )
            ChatViewer.objects.create(chat_id=user_record, sender=user.username, sender_type="User", message=text)
            while run.status != "completed":
                time.sleep(1)
                run = client.beta.threads.runs.retrieve(
                    thread_id=user_record.thread_id,
                    run_id=run.id
                )
                test_id = True
                print(run.status)
                # if test_id:
                if run.status == "incomplete":
                    user_record.needed_operator = 1
                    user_record2.needed_operator = 1
                    user_record.save()
                    user_record2.save()
                    remove_thread.delay(user_record.thread_id)
                    # textii = "Привет, я не смог ответить на сообщение пользователя --> " + update.message.text + ". Я соединил тебя с этим пользователем, попробуй ему объяснить. Напишите stopitnow тобы отключиться от пользователя."
                    # context.bot.send_message(chat_id=user_record2.user_id, text=textii)
                    # operator_def(update, context)
                    return print("AsstCanNotAnswer")
                elif run.status == "requires_action":
                    # function_res = plot_graph(run.required_action.submit_tool_outputs.tool_calls[0].function.arguments, update, context)
                    client.beta.threads.runs.submit_tool_outputs(
                        thread_id=user_record.thread_id,
                        run_id=run.id,
                        tool_outputs=[
                            {
                                "tool_call_id": run.required_action.submit_tool_outputs.tool_calls[0].id,
                                # "output": function_res
                            }
                        ]
                    )
            messages = client.beta.threads.messages.list(
                thread_id=user_record.thread_id
            )
            for Incomplete_word in Incomplete_word_massa:
                if Incomplete_word in messages.data[0].content[0].text.value:
                    user_record.needed_operator = 1
                    user_record2.needed_operator = 1
                    user_record.save()
                    user_record2.save()
                    remove_thread.delay(user_record.thread_id)
                    # textii = "Привет, я не смог ответить на сообщение пользователя --> " + update.message.text + ". Я соединил тебя с этим пользователем, попробуй ему объяснить. Напишите stopitnow тобы отключиться от пользователя."
                    # context.bot.send_message(chat_id=user_record2.user_id, text=textii)
                    # operator_def(update, context)
                    return print("AsstCanNotAnswer")
            ChatViewer.objects.create(chat_id=user_record, sender="ChatGPT", sender_type="ChatGPT", message=messages.data[0].content[0].text.value)
            return JsonResponse("success", safe=False)
            # update.message.reply_text(f"{messages.data[0].content[0].text.value}")

@csrf_exempt
def get_messages(request, chat_id):
    if request.method == 'GET':
        messages = ChatViewer.objects.filter(chat_id=chat_id).select_related('sender').order_by(
            'Message_Creation_Date')

        # Объединяем данные в один список
        combined_data = []

        for message in messages:
            combined_data.append({
                'type': 'message',
                'content': message.message,
                'sender': message.sender.username,  # Получаем username отправителя
                'creation_date': message.Message_Creation_Date
            })

        # Сортируем объединенные данные по дате создания
        combined_data = sorted(combined_data, key=lambda x: x['creation_date'])
        print(combined_data)
        return JsonResponse(combined_data, safe=False)