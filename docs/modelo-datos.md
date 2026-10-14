# Modelo de datos

Este diagrama refleja los modelos propios de las aplicaciones. `USER` es el modelo de usuarios que aporta Django; las tablas de permisos, sesiones y administración se generan automáticamente y no son modelos de negocio de MusicPro.

![Diagrama del modelo de datos de MusicPro](modelo-datos.svg)

```mermaid
%%{init: {"theme": "dark"}}%%
erDiagram
    USER ||--o| PROFILE : tiene
    USER ||--o| CART : posee
    CART ||--o{ CART_ITEM : contiene
    PRODUCT ||--o{ CART_ITEM : seleccionado
    CATEGORY o|--o{ PRODUCT : clasifica
    USER ||--o{ ORDER : realiza
    ORDER ||--o{ ORDER_ITEM : incluye
    PRODUCT ||--o{ ORDER_ITEM : vendido
    BEATPAY_WALLET o|--o{ TRANSACTION : registra
    TRANSACTION ||--o| VOUCHER : genera
    TRANSACTION o|--o| ORDER : respalda
    USER ||--o| BEATPAY_WALLET : posee
    USER ||--o| POINTS_WALLET : acumula
    POINTS_WALLET ||--o{ POINTS_LEDGER : registra
    SUPPLIER ||--o{ SUPPLIER_PRODUCT : ofrece
    PRODUCT ||--o{ SUPPLIER_PRODUCT : incluido
    SUPPLIER ||--o{ SUPPLIER_ORDER : recibe
    SUPPLIER_ORDER ||--o{ SUPPLIER_ORDER_ITEM : contiene
    PRODUCT ||--o{ SUPPLIER_ORDER_ITEM : solicitado
    USER o|--o{ FRAUD_LOG : origina
    USER ||--o{ NOTIFICATION : recibe
    VOUCHER o|--o{ NOTIFICATION : adjunta
    USER ||--o{ CHAT_MESSAGE : escribe

    USER {
        int id PK
        string username
        string password
        string first_name
        string last_name
        string email
        boolean is_staff
        boolean is_superuser
        boolean is_active
        datetime last_login
        datetime date_joined
    }
    PROFILE {
        int id PK
        int user_id FK,UK
        string rut UK
        string telefono
        string pais
        string moneda
        string bpass_hash
        string rol
        string estado
    }
    CATEGORY {
        int id PK
        string name
    }
    PRODUCT {
        int id PK
        int categoria_id FK
        string codigo UK
        string nombre
        decimal precio
        string descripcion
        string imagen
        int stock
        string ubicacion
    }
    CART {
        int id PK
        int user_id FK,UK
        datetime creado
        datetime actualizado
    }
    CART_ITEM {
        int id PK
        int cart_id FK
        int product_id FK
        int cantidad
    }
    ORDER {
        int id PK
        int user_id FK
        int transaction_id FK,UK
        decimal total
        string estado
        int puntos_usados
        decimal descuento_puntos
        datetime creada
    }
    ORDER_ITEM {
        int id PK
        int order_id FK
        int product_id FK
        int cantidad
        decimal precio_unitario
    }
    BEATPAY_WALLET {
        int id PK
        int user_id FK,UK
        string numero_tarjeta UK
        string token UK
        decimal saldo
        string estado
        datetime creada
    }
    TRANSACTION {
        int id PK
        int wallet_id FK
        decimal monto
        datetime fecha
        string concepto
        string tipo
        string resultado
        string referencia
        int folio UK
    }
    VOUCHER {
        int id PK
        int transaction_id FK,UK
        int usuario_id FK
        int folio
        datetime fecha
        decimal monto
        string concepto
        string resultado
        string tipo
        string pdf
    }
    POINTS_WALLET {
        int id PK
        int user_id FK,UK
        int puntos
        int puntos_canjeados
        datetime actualizado
    }
    POINTS_LEDGER {
        int id PK
        int wallet_id FK
        int cantidad
        string motivo
        datetime fecha
    }
    SUPPLIER {
        int id PK
        string nombre
        string contacto
        string telefono
        string email
        string direccion
        int tiempo_entrega_dias
        boolean activo
    }
    SUPPLIER_PRODUCT {
        int id PK
        int supplier_id FK
        int product_id FK
        decimal precio_mayorista
    }
    SUPPLIER_ORDER {
        int id PK
        int supplier_id FK
        decimal monto_total
        string estado
        string observacion
        datetime creada
    }
    SUPPLIER_ORDER_ITEM {
        int id PK
        int order_id FK
        int product_id FK
        int cantidad
        decimal precio_unitario
    }
    FRAUD_RULE {
        int id PK
        string nombre
        decimal umbral_monto
        boolean activa
    }
    FRAUD_LOG {
        int id PK
        int user_id FK
        string tipo
        string detalle
        decimal monto
        datetime fecha
        boolean resuelto
    }
    NOTIFICATION {
        int id PK
        int user_id FK
        int voucher_id FK
        string tipo
        string mensaje
        boolean leida
        datetime fecha
    }
    CHAT_MESSAGE {
        int id PK
        int user_id FK
        string remitente
        string texto
        datetime fecha
    }
```

`FK` indica clave foránea, `UK` una columna única y `PK` la clave primaria. Los productos pueden quedar sin categoría; una transacción puede existir sin billetera y una orden sin transacción. `SUPPLIER_PRODUCT` relaciona proveedores y productos, y su par proveedor/producto es único.

Para explicar el modelo en la evaluación, puedes partir por `CATEGORY` y `PRODUCT`: una categoría clasifica varios productos y el producto guarda código único, precio y stock. Luego muestra `ORDER` y `ORDER_ITEM`: esta tabla intermedia permite que una orden incluya varios productos y almacena la cantidad y el precio al momento de la compra.
