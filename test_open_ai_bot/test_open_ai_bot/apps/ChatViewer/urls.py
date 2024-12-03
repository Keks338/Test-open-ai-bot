from . import views
from django.urls import path, include

app_name = "ChatViewer"

urlpatterns = [
    path('', views.homePage, name='homePage'),
    path('add-new-chat/', views.create_new_chat),
    path('get-messages/<int:chat_id>/', views.get_messages),
]