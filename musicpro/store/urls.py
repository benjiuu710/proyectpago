from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('carrito/', views.carrito, name='carrito'),
    path('carrito/agregar/<int:pk>/', views.agregar_al_carrito, name='agregar'),
    path('checkout/', views.checkout, name='checkout'),
    path('orden/<int:pk>/', views.orden_detalle, name='orden'),
]
