from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import FraudLog, FraudRule
from users.models import Profile


@login_required
def monitoreo(request):
    logs = FraudLog.objects.order_by('-fecha')
    rules = FraudRule.objects.all()
    return render(request, 'fraud/monitoreo.html', {'logs': logs, 'rules': rules})


@login_required
def bloquear_cuenta(request):
    perfil, _ = Profile.objects.get_or_create(user=request.user)
    perfil.bloquear()
    if hasattr(request.user, 'wallet'):
        request.user.wallet.bloquear()
    messages.warning(request, 'Tu cuenta y tarjeta virtual fueron bloqueadas por anti-robo.')
    return redirect('store:inicio')
