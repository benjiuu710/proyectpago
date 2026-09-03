from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import PointsWallet, PointsLedger


@login_required
def mis_puntos(request):
    wallet, _ = PointsWallet.objects.get_or_create(user=request.user)
    historial = wallet.ledger.order_by('-fecha')
    return render(request, 'loyalty/puntos.html', {
        'wallet': wallet,
        'historial': historial,
    })
