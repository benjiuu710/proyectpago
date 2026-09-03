from django.db import models
from django.contrib.auth.models import User
from payments.models import Voucher


class Notification(models.Model):
    TIPO_CHOICES = [
        ('pago_ok', 'Pago aprobado'),
        ('pago_rechazado', 'Pago rechazado'),
        ('comprobante', 'Boucher/comprobante'),
        ('seguridad', 'Alertas de seguridad'),
        ('promocion', 'Promociones'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    tipo = models.CharField('Tipo', max_length=30, choices=TIPO_CHOICES)
    mensaje = models.TextField('Mensaje')
    voucher = models.ForeignKey(Voucher, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    leida = models.BooleanField('Leída', default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.get_tipo_display()}'

    def marcar_leida(self):
        self.leida = True
        self.save(update_fields=['leida'])


class ChatMessage(models.Model):
    """Mensajes del Bot de Atención 24/7."""
    REMITENTE_CHOICES = [
        ('usuario', 'Usuario'),
        ('bot', 'Bot'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    remitente = models.CharField('Remitente', max_length=10, choices=REMITENTE_CHOICES)
    texto = models.TextField('Texto')
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} [{self.remitente}]: {self.texto[:40]}'
