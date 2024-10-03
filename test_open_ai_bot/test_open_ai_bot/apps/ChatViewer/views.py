from django.shortcuts import render
from django.contrib.auth.models import User
from .models import ChatViewer
from ..test_open_ai_bot_app.models import BotUser

def homePage(request):
    Users = User.objects.all()
    Users2 = BotUser.objects.all()
    return render(request, "messanger/index.html", {
        "Users": Users,
        "Users2": Users2
    })

def homePage2(request, user_id):
    Users = User.objects.all()
    Users2 = BotUser.objects.all()
    Chats = ChatViewer.objects.filter(chat_id=user_id)
    return render(request, "messanger/index.html", {
        "Users": Users,
        "Users2": Users2,
        "Chats": Chats
    })
