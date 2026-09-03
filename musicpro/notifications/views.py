from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notification, ChatMessage
from .services import responder_bot


@login_required
def bandeja(request):
    notificaciones = Notification.objects.filter(user=request.user).order_by('-fecha')
    for n in notificaciones.filter(leida=False):
        n.marcar_leida()
    return render(request, 'notifications/bandeja.html', {'notificaciones': notificaciones})


@login_required
def bot_chat(request):
    historial = ChatMessage.objects.filter(user=request.user).order_by('fecha')
    if request.method == 'POST':
        texto = request.POST.get('mensaje', '')
        if texto.strip():
            respuesta = responder_bot(request.user, texto)
            messages.info(request, respuesta)
        return redirect('notifications:bot')
    return render(request, 'notifications/bot.html', {'historial': historial})
