from django.db import models
from django.contrib.auth.models import User
from payments.models import BeatPayWallet, Transaction
from loyalty.models import PointsWallet


class Category(models.Model):
    name = models.CharField('Categoría', max_length=60)

    def __str__(self):
        return self.name


class Product(models.Model):
    nombre = models.CharField('Nombre', max_length=120)
    codigo = models.CharField('Código de producto', max_length=30, unique=True)
    categoria = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    precio = models.DecimalField('Precio (CLP)', max_digits=12, decimal_places=2)
    descripcion = models.TextField('Descripción', blank=True, default='')
    imagen = models.ImageField('Imagen', upload_to='products/', null=True, blank=True)
    stock = models.PositiveIntegerField('Stock disponible', default=0)
    ubicacion = models.CharField('Ubicación', max_length=80, blank=True, default='')

    def __str__(self):
        return self.nombre


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Carrito de {self.user.username}'

    def total(self):
        return sum(item.subtotal() for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.product.precio * self.cantidad


class Order(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('pagada', 'Pagada'),
        ('despachada', 'Despachada'),
        ('cancelada', 'Cancelada'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    items = models.ManyToManyField(Product, through='OrderItem')
    total = models.DecimalField('Total', max_digits=12, decimal_places=2, default=0)
    estado = models.CharField('Estado', max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    puntos_usados = models.PositiveIntegerField('Puntos canjeados', default=0)
    descuento_puntos = models.DecimalField('Descuento por puntos', max_digits=12, decimal_places=2, default=0)
    creada = models.DateTimeField(auto_now_add=True)
    transaction = models.OneToOneField(Transaction, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'Orden {self.pk} - {self.user.username}'

    def recalcular(self):
        self.total = sum(item.subtotal() for item in self.order_items.all())
        self.save(update_fields=['total'])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)

    def subtotal(self):
        return self.precio_unitario * self.cantidad
