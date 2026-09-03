from django.contrib import admin
from .models import PointsWallet, PointsLedger


@admin.register(PointsWallet)
class PointsWalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'puntos', 'puntos_canjeados')


@admin.register(PointsLedger)
class PointsLedgerAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'cantidad', 'motivo', 'fecha')
