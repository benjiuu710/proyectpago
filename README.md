# MusicPro — Sistema de Pago BeatPay

Backend Django de la plataforma MusicPro con sistema de pago (tarjeta virtual BeatPay),
antifraude, bot 24/7, fidelización por puntos, gestión de proveedores y comprobantes/bouchers.

## Estructura

```
proyect/
└── musicpro/
    ├── users/          # Usuarios, perfiles, roles
    ├── store/          # Catálogo, carrito, pedidos (checkout con puntos + pago)
    ├── payments/       # Tarjeta virtual BeatPay, transacciones, comprobantes
    ├── loyalty/        # Programa de puntos y recompensas
    ├── suppliers/      # Proveedores, catálogo mayorista, órdenes de compra
    ├── fraud/          # Antifraude y anti-robo
    ├── notifications/  # Bandeja de notificaciones + Bot 24/7
    └── templates/      # Plantillas HTML
```

## Instalación

```powershell
# Ejecuta estos comandos desde la carpeta proyect
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Configura las credenciales de tu MySQL local en esta terminal.
$env:DB_NAME = 'musicpro'
$env:DB_USER = 'root'
$env:DB_PASSWORD = 'tu_clave_local'
$env:DB_HOST = '127.0.0.1'
$env:DB_PORT = '3306'

# Crea antes la base musicpro en MySQL y luego prepara las tablas.
python manage.py migrate
$env:DJANGO_DEBUG = 'true'
python manage.py createsuperuser
python setup_demo.py
python manage.py runserver
```

Abre http://127.0.0.1:8000/. El panel administrativo propio está en
http://127.0.0.1:8000/gestion/. El superusuario creado con `createsuperuser`
inicia sesión desde `/usuarios/login/` para acceder al panel.

## Funcionalidades

- **Tienda y carrito**: catálogo, agregar al carrito, checkout.
- **Administración propia** (`/gestion/`): catálogo, categorías, usuarios, ventas y reportes ORM; los perfiles Administrador y Operador tienen permisos distintos.
- **Estado de productos**: el catálogo y la API solo ofrecen productos activos; el panel permite activarlos o desactivarlos.
- **Pago BeatPay**: tarjeta virtual con saldo, recarga, y validación instantánea de saldo.
- **Puntos de fidelización**: acumulas 1 punto por cada $1.000 CLP; 1 punto = $10 CLP de descuento en el checkout.
- **Proveedores**: catálogo al por mayor; al comprar valida fondos automáticamente y, si falta saldo,
  cancela y notifica con comprobante de rechazo.
- **Antifraude**: bloqueo preventivo por monto inusual y congelación de cuenta/tarjeta (anti-robo).
- **Bot 24/7** (`/notificaciones/bot/`): consulta saldo, estado de pedido, puntos o bloquea tarjeta por emergencia.
- **Notificaciones + Boucher**: cada operación aprobada o rechazada genera comprobante y notificación.

## Accesos rápidos

- `/` — Tienda
- `/carrito/` — Carrito
- `/checkout/` — Checkout con pago
- `/pagos/tarjeta/` — Tarjeta BeatPay y saldo
- `/pagos/comprobantes/` — Bouchers
- `/lealtad/puntos/` — Puntos de fidelización
- `/proveedores/` — Proveedores
- `/fraude/monitoreo/` — Antifraude
- `/notificaciones/` — Bandeja
- `/notificaciones/bot/` — Bot 24/7
- `/gestion/` — Panel administrativo propio
- `/gestion/reportes/` — Reportes ORM de Tienda

## Nota sobre el sistema de pago

El pago se procesa desde la "tarjeta virtual BeatPay" (saldo en CLP almacenado en `BeatPayWallet`).
`payments/services.py` contiene el núcleo: valida saldo, aplica antifraude, debita, crea la transacción
y genera voucher + notificación.

La conexión predeterminada es MySQL local y se configura con las variables `DB_NAME`, `DB_USER`,
`DB_PASSWORD`, `DB_HOST` y `DB_PORT`. Para ejecutar pruebas sin un servidor MySQL, establece
`DB_ENGINE=django.db.backends.sqlite3`; en ese modo se usa `musicpro/db.sqlite3`.

Para ejecutar las pruebas automatizadas del proyecto:

```powershell
python manage.py test backoffice users store payments fraud
```
