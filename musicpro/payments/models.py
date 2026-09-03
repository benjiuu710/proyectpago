from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User


class BeatPayWallet(models.Model):
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('bloqueada', 'Bloqueada por cliente o sistema anti-robo'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    numero_tarjeta = models.CharField('Número de tarjeta virtual', max_length=19, unique=True)
    token = models.CharField('Token', max_length=64, unique=True)
    saldo = models.DecimalField('Saldo (CLP)', max_digits=12, decimal_places=2, default=0)
    estado = models.CharField('Estado', max_length=20, choices=ESTADO_CHOICES, default='activa')
    creada = models.DateTimeField('Fecha de creación', auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.numero_tarjeta}'

    def cargar_saldo(self, monto):
        monto = Decimal(str(monto))
        self.saldo += monto
        self.save(update_fields=['saldo'])

    def debitar(self, monto):
        monto = Decimal(str(monto))
        self.saldo -= monto
        self.save(update_fields=['saldo'])

    def bloquear(self):
        self.estado = 'bloqueada'
        self.save(update_fields=['estado'])

    def habilitar(self):
        self.estado = 'activa'
        self.save(update_fields=['estado'])


class Transaction(models.Model):
    TIPO_CHOICES = [
        ('compra_cliente', 'Compra de cliente'),
        ('pago_proveedor', 'Pago a proveedor'),
        ('recarga', 'Recarga de saldo'),
    ]
    RESULTADO_CHOICES = [
        ('aprobada', 'Aprobada'),
        ('rechazada_saldo', 'Rechazada por saldo insuficiente'),
        ('rechazada_fraude', 'Rechazada por fraude'),
        ('cancelada', 'Cancelada'),
    ]

    wallet = models.ForeignKey(BeatPayWallet, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    monto = models.DecimalField('Monto', max_digits=12, decimal_places=2)
    fecha = models.DateTimeField('Fecha/Hora', auto_now_add=True)
    concepto = models.CharField('Comercio/Origen', max_length=120, blank=True, default='')
    tipo = models.CharField('Tipo de operación', max_length=30, choices=TIPO_CHOICES)
    resultado = models.CharField('Resultado', max_length=30, choices=RESULTADO_CHOICES, default='aprobada')
    referencia = models.CharField('Referencia orden', max_length=60, blank=True, default='')
    folio = models.PositiveIntegerField('Folio', unique=True)

    def __str__(self):
        return f'Transacción {self.folio} - {self.get_tipo_display()} - {self.monto}'

    def guardar_voucher(self):
        voucher = Voucher(
            transaction=self,
            folio=self.folio,
            monto=self.monto,
            concepto=self.concepto,
            resultado=self.resultado,
            tipo=self.tipo,
            usuario=self.wallet.user if self.wallet else None,
        )
        voucher.save()
        return voucher


class Voucher(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='voucher')
    folio = models.PositiveIntegerField('Folio único')
    fecha = models.DateTimeField('Fecha', auto_now_add=True)
    monto = models.DecimalField('Monto', max_digits=12, decimal_places=2)
    concepto = models.CharField('Concepto', max_length=120, default='')
    resultado = models.CharField('Resultado', max_length=30)
    tipo = models.CharField('Tipo', max_length=30)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    pdf = models.FileField('Comprobante PDF', upload_to='vouchers/', null=True, blank=True)

    def __str__(self):
        return f'Comprobante {self.folio}'
