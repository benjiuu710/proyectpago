#!/usr/bin/env python
"""Script de configuración e inicialización de MusicPro.

Crea la base de datos, el superusuario y datos de demostración.
Ejecutar estando dentro del entorno virtual y con la carpeta musicpro activa.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'musicpro.settings')
django.setup()

from django.contrib.auth.models import User
from store.models import Category, Product
from suppliers.models import Supplier, SupplierProduct
from payments.services import obtener_wallet, recargar_saldo
from loyalty.models import PointsWallet
from fraud.models import FraudRule


def main():
    admin_password = os.environ.get('DEMO_ADMIN_PASSWORD')
    client_password = os.environ.get('DEMO_CLIENT_PASSWORD')
    if not admin_password or not client_password:
        raise RuntimeError('Define DEMO_ADMIN_PASSWORD y DEMO_CLIENT_PASSWORD antes de ejecutar setup_demo.py.')

    # Superusuario
    if User.objects.filter(username='admin').exists():
        print('Superusuario admin ya existe.')
    else:
        User.objects.create_superuser('admin', 'admin@musicpro.cl', admin_password)
        print('Superusuario creado: admin')

    # Categorías
    cat_instrumentos, _ = Category.objects.get_or_create(name='Instrumentos')
    cat_audio, _ = Category.objects.get_or_create(name='Audio')
    cat_accesorios, _ = Category.objects.get_or_create(name='Accesorios')

    # Productos
    productos = [
        ('Guitarra Eléctrica Strat', 'MP-001', cat_instrumentos, 350000, 'Guitarra eléctrica estándar.', 12),
        ('Teclado de 61 teclas', 'MP-002', cat_instrumentos, 180000, 'Teclado portátil con 200 sonidos.', 8),
        ('Batería acústica 5 piezas', 'MP-003', cat_instrumentos, 520000, 'Batería completa con platillos.', 4),
        ('Parlante Bluetooth 50W', 'MP-004', cat_audio, 95000, 'Parlante portátil de alto rendimiento.', 20),
        ('Micrófono dinámico', 'MP-005', cat_audio, 45000, 'Micrófono para voces e instrumentos.', 30),
        ('Cable de audio 6m', 'MP-006', cat_accesorios, 8000, 'Cable de instrumento blindado.', 50),
        ('Atril de partitura', 'MP-007', cat_accesorios, 15000, 'Atril metálico plegable.', 25),
    ]
    for nombre, codigo, cat, precio, desc, stock in productos:
        Product.objects.get_or_create(
            codigo=codigo,
            defaults=dict(nombre=nombre, categoria=cat, precio=precio,
                          descripcion=desc, stock=stock),
        )
    print(f'{len(productos)} productos registrados.')

    # Proveedor
    prov, created = Supplier.objects.get_or_create(
        nombre='Distribuidora Música Total',
        defaults=dict(contacto='Ventas', telefono='+56912345678',
                      email='ventas@musictotal.cl', tiempo_entrega_dias=5),
    )
    if created:
        for p in Product.objects.all():
            SupplierProduct.objects.get_or_create(
                supplier=prov, product=p,
                defaults=dict(precio_mayorista=round(float(p.precio) * 0.7, 2)),
            )
        print(f'Catálogo del proveedor {prov.nombre} cargado.')

    # Regla antifraude
    FraudRule.objects.get_or_create(
        nombre='Monto inusual',
        defaults=dict(umbral_monto=1000000),
    )

    # Usuario cliente de demostración con saldo
    if not User.objects.filter(username='cliente').exists():
        u = User.objects.create_user('cliente', 'cliente@musicpro.cl', client_password)
        u.profile.rut = '11.111.111-1'
        u.profile.telefono = '+56900000000'
        u.profile.save()
        recargar_saldo(u, 500000)
        PointsWallet.objects.get_or_create(user=u, defaults={'puntos': 100})
        print('Usuario cliente creado: cliente (saldo $500.000, 100 pts)')

    print('\n¡Configuración lista!')
    print('  Admin:    admin')
    print('  Cliente:  cliente')


if __name__ == '__main__':
    main()
