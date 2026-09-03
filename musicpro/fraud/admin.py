from django.contrib import admin
from .models import FraudRule, FraudLog


@admin.register(FraudRule)
class FraudRuleAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'umbral_monto', 'activa')


@admin.register(FraudLog)
class FraudLogAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'user', 'monto', 'fecha', 'resuelto')
    list_filter = ('tipo', 'resuelto')
