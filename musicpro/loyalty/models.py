from django.db import models
from django.contrib.auth.models import User


class PointsWallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='points_wallet')
    puntos = models.PositiveIntegerField('Puntos acumulados', default=0)
    puntos_canjeados = models.PositiveIntegerField('Puntos canjeados', default=0)
    actualizado = models.DateTimeField('Última actualización', auto_now=True)

    def __str__(self):
        return f'{self.user.username} - {self.puntos} pts'

    def acumular(self, cantidad):
        self.puntos += cantidad
        self.save(update_fields=['puntos'])

    def canjear(self, cantidad):
        if cantidad <= self.puntos:
            self.puntos -= cantidad
            self.puntos_canjeados += cantidad
            self.save(update_fields=['puntos', 'puntos_canjeados'])
            return cantidad
        return 0


class PointsLedger(models.Model):
    wallet = models.ForeignKey(PointsWallet, on_delete=models.CASCADE, related_name='ledger')
    cantidad = models.IntegerField('Cantidad (+/-)')
    motivo = models.CharField('Motivo', max_length=120)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.wallet.user.username} - {self.cantidad:+d}'
