from django.urls import path
from . import views

app_name = 'suppliers'

urlpatterns = [
    path('', views.listar_proveedores, name='proveedores'),
    path('<int:pk>/', views.detalle_proveedor, name='detalle'),
    path('ordenes/', views.lista_ordenes, name='ordenes'),
]
