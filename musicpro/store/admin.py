from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem


class CartItemInline(admin.TabularInline):
    model = CartItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'categoria', 'precio', 'stock')
    list_filter = ('categoria',)
    search_fields = ('nombre', 'codigo')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = (CartItemInline,)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderItemInline,)
    list_display = ('pk', 'user', 'total', 'estado', 'creada')
    list_filter = ('estado',)
