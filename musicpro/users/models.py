from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    COUNTRY_CURRENCY = {
        'CL': ('CLP', '$'), 'AR': ('ARS', '$'), 'BR': ('BRL', 'R$'),
        'CA': ('CAD', 'C$'), 'CO': ('COP', '$'), 'ES': ('EUR', '€'),
        'GB': ('GBP', '£'), 'JP': ('JPY', '¥'), 'MX': ('MXN', '$'),
        'PE': ('PEN', 'S/'), 'US': ('USD', '$'),
    }
    ROL_CHOICES = [
        ('cliente', 'Cliente'),
        ('admin', 'Administrador'),
        ('encargado', 'Encargado de Proveedores'),
    ]
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('bloqueada', 'Bloqueada por seguridad/anti-robo'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    rut = models.CharField('RUT', max_length=12, unique=True, blank=True, null=True)
    telefono = models.CharField('Teléfono', max_length=20, blank=True, null=True)
    pais = models.CharField('País', max_length=2, blank=True, default='CL')
    moneda = models.CharField('Moneda', max_length=3, blank=True, default='CLP')
    bpass_hash = models.CharField('BPass protegido', max_length=128, blank=True, default='')
    rol = models.CharField('Rol', max_length=20, choices=ROL_CHOICES, default='cliente')
    estado = models.CharField('Estado de la cuenta', max_length=20, choices=ESTADO_CHOICES, default='activa')

    def __str__(self):
        return f'{self.user.username} - {self.get_rol_display()}'

    def bloquear(self):
        self.estado = 'bloqueada'
        self.save(update_fields=['estado'])

    def habilitar(self):
        self.estado = 'activa'
        self.save(update_fields=['estado'])

    @property
    def simbolo_moneda(self):
        return self.COUNTRY_CURRENCY.get(self.pais, ('CLP', '$'))[1]


@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
