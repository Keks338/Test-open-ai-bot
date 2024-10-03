from . import views
from django.urls import path, include

app_name = "ChatViewer"

urlpatterns = [
    path('', views.homePage, name='homePage'),
    path('Chat/<int:user_id>/', views.homePage2, name='homePage2'),
]