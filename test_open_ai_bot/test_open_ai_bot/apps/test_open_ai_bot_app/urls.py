from . import views
from django.urls import path, include

app_name = "test_open_ai_bot_app"

urlpatterns = [
    path('webhook/', views.webhook, name='webhook'),
]