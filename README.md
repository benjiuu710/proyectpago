# 🎵 MusicPro — Sistema de Pago BeatPay

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
# 1. Crea tu entorno virtual (tú lo harás) y actívalo
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Instala dependencias
pip install -r requirements.txt

# 3. Entra a la carpeta del proyecto
cd musicpro

# 4. Crea las migraciones y la base de datos
python manage.py makemigrations users store payments loyalty suppliers fraud notifications
python manage.py migrate

# 5. Carga datos de demostración (superusuario, productos, proveedor, cliente)
python ../setup_demo.py

# 6. Corre el servidor
python manage.py runserver
```

Abre tu http

## Usuarios de demostración

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| admin   | admin123   | Superusuario (panel /admin) |
| cliente | cliente123 | Cliente con saldo $500.000 y 100 pts |

## Funcionalidades

- **Tienda y carrito**: catálogo, agregar al carrito, checkout.
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
- `/admin/` — Panel de administración

## Nota sobre el sistema de pago

El pago se procesa desde la "tarjeta virtual BeatPay" (saldo en CLP almacenado en `BeatPayWallet`).
`payments/services.py` contiene el núcleo: valida saldo, aplica antifraude, debita, crea la transacción
y genera voucher + notificación.
