#!/usr/bin/env python
"""Script de configuración e inicialización de MusicPro.

Crea datos de demostración y, opcionalmente, cuentas de prueba.
Ejecutar desde la carpeta proyect con el entorno virtual activado.
"""
import os
import sys
import django
from faker import Faker

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'musicpro'))
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

    # Superusuario
    if User.objects.filter(username='admin').exists():
        print('Superusuario admin ya existe.')
    elif admin_password:
        User.objects.create_superuser('admin', 'admin@musicpro.cl', admin_password)
        print('Superusuario creado: admin')
    else:
        print('No se creó admin. Usa manage.py createsuperuser o define DEMO_ADMIN_PASSWORD.')

    # Categorías
    cat_instrumentos, _ = Category.objects.get_or_create(name='Instrumentos')
    cat_audio, _ = Category.objects.get_or_create(name='Audio')
    cat_accesorios, _ = Category.objects.get_or_create(name='Accesorios')
    fake = Faker('es_CL')
    fake.seed_instance(42)

    # Productos
    productos = [
        ('Yamaha Pacifica 112V', 'MP-001', cat_instrumentos, 459990, 'Guitarra eléctrica de seis cuerdas con configuración HSS.', 'Sala de guitarras'),
        ('Fender Player II Stratocaster', 'MP-002', cat_instrumentos, 1349990, 'Guitarra eléctrica Stratocaster de la serie Player II.', 'Sala de guitarras'),
        ("Squier Classic Vibe '60s Stratocaster", 'MP-003', cat_instrumentos, 699990, 'Guitarra eléctrica inspirada en las Stratocaster de los años sesenta.', 'Sala de guitarras'),
        ('Yamaha PSR-E383', 'MP-004', cat_instrumentos, 299990, 'Teclado portátil de 61 teclas para estudio y presentaciones.', 'Sala de teclados'),
        ('Casio CT-S300', 'MP-005', cat_instrumentos, 229990, 'Teclado portátil Casiotone de 61 teclas con respuesta táctil.', 'Sala de teclados'),
        ('Yamaha DTX402K', 'MP-006', cat_instrumentos, 699990, 'Batería electrónica de la serie DTX402.', 'Sala de baterías'),
        ('Pearl Roadshow RS505C', 'MP-007', cat_instrumentos, 899990, 'Batería acústica Roadshow de cinco piezas.', 'Sala de baterías'),
        ('JBL Charge 5', 'MP-008', cat_audio, 199990, 'Parlante Bluetooth portátil resistente al agua.', 'Sala de audio'),
        ('Shure SM58', 'MP-009', cat_audio, 129990, 'Micrófono dinámico cardioide para voces.', 'Sala de audio'),
        ('Audio-Technica ATH-M50x', 'MP-010', cat_audio, 179990, 'Audífonos de monitoreo profesional circumaurales.', 'Sala de audio'),
        ('BOSS DS-1 Distortion', 'MP-011', cat_accesorios, 99990, 'Pedal de distorsión para guitarra eléctrica.', 'Bodega de pedales'),
        ("D'Addario EXL110", 'MP-012', cat_accesorios, 9990, 'Juego de cuerdas XL Nickel Wound para guitarra eléctrica, calibre 10-46.', 'Bodega de cuerdas'),
    ]
    for nombre, codigo, cat, precio, desc, ubicacion in productos:
        Product.objects.update_or_create(
            codigo=codigo,
            defaults=dict(
                nombre=nombre,
                categoria=cat,
                precio=precio,
                descripcion=desc,
                stock=fake.random_int(min=2, max=20),
                ubicacion=ubicacion,
            ),
        )
    print(f'{len(productos)} productos registrados.')

    # Proveedor
    prov, created = Supplier.objects.get_or_create(
        nombre='Distribuidora Música Total',
        defaults=dict(contacto='Ventas', telefono='+56912345678',
                      email='ventas@musictotal.cl', tiempo_entrega_dias=5),
    )
    for p in Product.objects.filter(codigo__startswith='MP-'):
        SupplierProduct.objects.update_or_create(
            supplier=prov,
            product=p,
            defaults=dict(precio_mayorista=round(float(p.precio) * 0.7, 2)),
        )
    if created:
        print(f'Catálogo del proveedor {prov.nombre} cargado.')

    # Regla antifraude
    FraudRule.objects.get_or_create(
        nombre='Monto inusual',
        defaults=dict(umbral_monto=1000000),
    )

    # Usuario cliente de demostración con saldo
    if not User.objects.filter(username='cliente').exists():
        if client_password:
            u = User.objects.create_user('cliente', 'cliente@musicpro.cl', client_password)
            u.profile.rut = '11.111.111-1'
            u.profile.telefono = '+56900000000'
            u.profile.save()
            recargar_saldo(u, 500000)
            PointsWallet.objects.get_or_create(user=u, defaults={'puntos': 100})
            print('Usuario cliente creado: cliente (saldo $500.000, 100 pts)')
        else:
            print('No se creó cliente. Define DEMO_CLIENT_PASSWORD si necesitas esa cuenta.')

    print('\n¡Configuración lista!')


if __name__ == '__main__':
    main()
