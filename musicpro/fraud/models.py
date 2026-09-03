from django.db import models
from django.contrib.auth.models import User


class FraudRule(models.Model):
    """Reglas de riesgo configurables."""
    nombre = models.CharField('Nombre de la regla', max_length=80)
    umbral_monto = models.DecimalField('Umbral de monto sospechoso (CLP)', max_digits=12, decimal_places=2, default=0)
    activa = models.BooleanField('Activa', default=True)

    def __str__(self):
        return self.nombre


class FraudLog(models.Model):
    """Registro de intentos sospechosos."""
    TIPO_CHOICES = [
        ('monto_inusual', 'Monto inusual'),
        ('intentos_fallidos', 'Múltiples intentos fallidos'),
        ('bloqueo_preventivo', 'Bloqueo preventivo'),
        ('tarjeta_reportada', 'Tarjeta reportada/robada'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fraud_logs', null=True, blank=True)
    tipo = models.CharField('Tipo de alerta', max_length=30, choices=TIPO_CHOICES)
    detalle = models.TextField('Detalle')
    monto = models.DecimalField('Monto implicado', max_digits=12, decimal_places=2, default=0)
    fecha = models.DateTimeField(auto_now_add=True)
    resuelto = models.BooleanField('Resuelto', default=False)

    def __str__(self):
        return f'{self.get_tipo_display()} - {self.user}'
