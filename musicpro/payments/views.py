from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import BeatPayWallet, Voucher
from .services import obtener_wallet, recargar_saldo


@login_required
def mi_tarjeta(request):
    wallet = obtener_wallet(request.user)
    transacciones = wallet.transactions.order_by('-fecha')
    return render(request, 'payments/tarjeta.html', {
        'wallet': wallet,
        'transacciones': transacciones,
    })


@login_required
def recargar(request):
    if request.method == 'POST':
        monto = request.POST.get('monto')
        try:
            monto = Decimal(str(monto))
            if monto <= 0:
                raise ValueError
        except (InvalidOperation, TypeError, ValueError):
            messages.error(request, 'Ingresa un monto válido.')
            return redirect('payments:tarjeta')
        txn = recargar_saldo(request.user, monto)
        messages.success(request, f'Recarga de {monto} CLP exitosa. Folio {txn.folio}.')
        return redirect('payments:tarjeta')
    return redirect('payments:tarjeta')


@login_required
def comprobantes(request):
    vouchers = Voucher.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'payments/comprobantes.html', {'vouchers': vouchers})


@login_required
@require_POST
def bloquear_tarjeta(request):
    wallet = obtener_wallet(request.user)
    accion = request.POST.get('accion', 'bloquear')
    if accion == 'habilitar':
        wallet.habilitar()
        messages.success(request, 'Tarjeta habilitada nuevamente.')
    elif accion == 'bloquear':
        wallet.bloquear()
        messages.success(request, 'Tarjeta bloqueada por anti-robo.')
    else:
        messages.error(request, 'Acción de tarjeta no válida.')
    return redirect('payments:tarjeta')
