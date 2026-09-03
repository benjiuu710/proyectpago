from django.urls import path
from . import views

app_name = 'fraud'

urlpatterns = [
    path('monitoreo/', views.monitoreo, name='monitoreo'),
    path('bloquear-cuenta/', views.bloquear_cuenta, name='bloquear_cuenta'),
]
