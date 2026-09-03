from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('tarjeta/', views.mi_tarjeta, name='tarjeta'),
    path('recargar/', views.recargar, name='recargar'),
    path('comprobantes/', views.comprobantes, name='comprobantes'),
    path('bloquear/', views.bloquear_tarjeta, name='bloquear'),
]
