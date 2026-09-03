from django.contrib import admin
from .models import BeatPayWallet, Transaction, Voucher


@admin.register(BeatPayWallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'numero_tarjeta', 'saldo', 'estado')
    list_filter = ('estado',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('folio', 'wallet', 'monto', 'tipo', 'resultado', 'fecha')
    list_filter = ('tipo', 'resultado')


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ('folio', 'fecha', 'monto', 'tipo', 'resultado', 'usuario')
