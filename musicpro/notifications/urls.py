from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.bandeja, name='bandeja'),
    path('bot/', views.bot_chat, name='bot'),
]
