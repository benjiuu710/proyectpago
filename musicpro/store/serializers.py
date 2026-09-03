from rest_framework import serializers

from .models import Order, OrderItem, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'nombre', 'codigo', 'categoria', 'precio', 'descripcion', 'stock', 'ubicacion')


class OrderItemSerializer(serializers.ModelSerializer):
    producto = serializers.CharField(source='product.nombre', read_only=True)

    class Meta:
        model = OrderItem
        fields = ('producto', 'cantidad', 'precio_unitario')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='order_items', many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'total', 'estado', 'creada', 'items')