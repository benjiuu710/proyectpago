from django.contrib import admin
from .models import Notification, ChatMessage


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo', 'leida', 'fecha')
    list_filter = ('tipo', 'leida')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'remitente', 'texto', 'fecha')
