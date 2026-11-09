from django.urls import path

from . import views

app_name = 'backoffice'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('productos/', views.product_list, name='products'),
    path('productos/nuevo/', views.product_form, name='product_create'),
    path('productos/<int:pk>/editar/', views.product_form, name='product_edit'),
    path('productos/<int:pk>/eliminar/', views.product_delete, name='product_delete'),
    path('categorias/', views.category_list, name='categories'),
    path('categorias/nueva/', views.category_form, name='category_create'),
    path('categorias/<int:pk>/editar/', views.category_form, name='category_edit'),
    path('categorias/<int:pk>/eliminar/', views.category_delete, name='category_delete'),
    path('usuarios/', views.user_list, name='users'),
    path('usuarios/nuevo/', views.user_form, name='user_create'),
    path('usuarios/<int:pk>/editar/', views.user_form, name='user_edit'),
    path('usuarios/<int:pk>/estado/', views.user_toggle_active, name='user_toggle_active'),
    path('ventas/', views.order_list, name='orders'),
    path('ventas/nueva/', views.order_form, name='order_create'),
    path('ventas/<int:pk>/editar/', views.order_form, name='order_edit'),
    path('ventas/<int:pk>/eliminar/', views.order_delete, name='order_delete'),
    path('ventas/<int:pk>/estado/', views.order_status, name='order_status'),
    path('reportes/', views.reports, name='reports'),
]