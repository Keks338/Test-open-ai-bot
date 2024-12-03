from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.models import User
from .models import ChatViewer
from django.views.decorators.csrf import csrf_exempt
from ..test_open_ai_bot_app.models import BotUser
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

def homePage(request):
    user = request.user
    Users = User.objects.all()
    Users2 = BotUser.objects.all()
    Chats = ChatViewer.objects.filter(chat_id=user.id)
    return render(request, "messanger/index2.html", {
        "current_user": user,
        "Users": Users,
        "Users2": Users2,
        "Chats": Chats
    })
@csrf_exempt
def create_new_chat(request):
    if request.method == "POST":
        user = request.user
        thread = client.beta.threads.create()
        BotUser.objects.create(user_id = user, thread_id = thread.id)
        message="success"
        return JsonResponse(message, safe=False)

@csrf_exempt
def get_messages(request, chat_id):
    if request.method == 'GET':
        messages = ChatViewer.objects.filter(chat_id=chat_id).order_by(
            'Message_Creation_Date')

        # Объединяем данные в один список
        combined_data = []

        for message in messages:
            combined_data.append({
                'type': message.message_type,
                'content': message.message,
                'sender': message.sender,  # Получаем username отправителя
                'creation_date': message.Message_Creation_Date,
                'image': message.image.url if message.image else None,
            })

        # Сортируем объединенные данные по дате создания
        combined_data = sorted(combined_data, key=lambda x: x['creation_date'])
        return JsonResponse(combined_data, safe=False)