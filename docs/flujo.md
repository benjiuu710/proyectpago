# Flujo principal de MusicPro

El proyecto seleccionado corresponde a **Sucursal y Punto de Venta**, con integración de BeatPay y fidelización.

```mermaid
flowchart TD
    A[Inicio] --> B{Usuario autenticado?}
    B -- No --> C[Bienvenida]
    C --> D[Registro o inicio de sesión]
    D --> B
    B -- Si --> E[Catálogo de productos]
    E --> F{Producto disponible?}
    F -- No --> E
    F -- Si --> G[Agregar al carrito]
    G --> H[Revisar carrito]
    H --> I{Confirmar compra?}
    I -- No --> E
    I -- Si --> J[Validar BPass y stock]
    J --> K{Datos válidos?}
    K -- No --> H
    K -- Si --> L[Aplicar puntos opcionales]
    L --> M[Validar saldo y antifraude]
    M --> N{Pago aprobado?}
    N -- No --> O[Notificar rechazo]
    O --> H
    N -- Si --> P[Crear orden y descontar stock]
    P --> Q[Generar transacción, voucher y notificación]
    Q --> R[Consultar detalle de orden]
```

## Rutas principales

- `/` muestra el catálogo y la bienvenida.
- `/usuarios/login/` y `/usuarios/registro/` gestionan el acceso.
- `/carrito/` permite revisar la selección.
- `/checkout/` valida BPass, stock, puntos, saldo y antifraude.
- `/pagos/comprobantes/` muestra los comprobantes.
- `/api/productos/` expone el CRUD de productos con escritura administrativa.
- `/api/pedidos/` devuelve los pedidos del usuario autenticado.
