from django.db import models
from store.models import Product


class Supplier(models.Model):
    nombre = models.CharField('Nombre de la empresa', max_length=120)
    contacto = models.CharField('Contacto', max_length=120, blank=True, default='')
    telefono = models.CharField('Teléfono', max_length=20, blank=True, default='')
    email = models.EmailField('Email', blank=True, default='')
    direccion = models.CharField('Dirección', max_length=160, blank=True, default='')
    tiempo_entrega_dias = models.PositiveIntegerField('Tiempo de entrega (días)', default=0)
    activo = models.BooleanField('Activo', default=True)

    def __str__(self):
        return self.nombre


class SupplierProduct(models.Model):
    """Catálogo del proveedor: precio al por mayor."""
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='catalog')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    precio_mayorista = models.DecimalField('Precio al por mayor', max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ('supplier', 'product')

    def __str__(self):
        return f'{self.supplier.nombre} - {self.product.nombre}'


class SupplierOrder(models.Model):
    ESTADO_CHOICES = [
        ('solicitada', 'Solicitada'),
        ('pagada', 'Pagada'),
        ('recibida', 'Recibida'),
        ('rechazada', 'Rechazada por saldo insuficiente'),
    ]

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='orders')
    monto_total = models.DecimalField('Monto total', max_digits=12, decimal_places=2, default=0)
    estado = models.CharField('Estado', max_length=20, choices=ESTADO_CHOICES, default='solicitada')
    observacion = models.CharField('Observación', max_length=200, blank=True, default='')
    creada = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Orden a {self.supplier.nombre} - {self.monto_total}'

    def recalcular(self):
        self.monto_total = sum(item.subtotal() for item in self.items.all())
        self.save(update_fields=['monto_total'])


class SupplierOrderItem(models.Model):
    order = models.ForeignKey(SupplierOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField('Precio unitario', max_digits=12, decimal_places=2)

    def subtotal(self):
        return self.precio_unitario * self.cantidad
