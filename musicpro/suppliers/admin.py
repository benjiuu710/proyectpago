from django.contrib import admin
from .models import Supplier, SupplierProduct, SupplierOrder, SupplierOrderItem


class SupplierProductInline(admin.TabularInline):
    model = SupplierProduct


class SupplierOrderItemInline(admin.TabularInline):
    model = SupplierOrderItem


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    inlines = (SupplierProductInline,)
    list_display = ('nombre', 'tiempo_entrega_dias', 'activo')


@admin.register(SupplierOrder)
class SupplierOrderAdmin(admin.ModelAdmin):
    inlines = (SupplierOrderItemInline,)
    list_display = ('pk', 'supplier', 'monto_total', 'estado', 'creada')
    list_filter = ('estado',)
