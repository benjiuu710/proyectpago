from django.urls import path
from . import views

app_name = 'loyalty'

urlpatterns = [
    path('puntos/', views.mis_puntos, name='puntos'),
]
