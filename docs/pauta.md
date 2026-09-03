# Trazabilidad con la pauta

| Indicador | Evidencia en el proyecto | Estado |
|---|---|---|
| 1.1.1 Identifica variables y operaciones | Modelos `Product`, `Cart`, `Order`, `BeatPayWallet` y sus relaciones; validaciones de stock, saldo y BPass en las vistas | Cumplido |
| 1.1.2 Codifica instrucciones, estructuras y operadores | Vistas con condicionales, bucles, filtros ORM, redirecciones y navegación por rutas nombradas | Cumplido |
| 1.1.3 Usa paquetes externos | Django REST Framework, SimpleJWT y Pillow declarados en `requirements.txt`; Bootstrap 5 en las plantillas | Cumplido |
| 1.1.4 Implementa Django | Proyecto Django operativo, apps registradas, URLs, vistas, plantillas y migraciones | Cumplido |
| 2.1.1 Conexión a base de datos | SQLite configurada en `settings.py` y migraciones de todas las apps | Cumplido |
| 2.1.2 Administrador Django | Modelos registrados en `admin.py`, incluyendo usuarios, perfiles, productos, carritos y órdenes | Cumplido |
| 2.1.3 Operaciones CRUD | CRUD administrativo de modelos y CRUD de productos en `/api/productos/`, con escritura restringida a administradores | Cumplido |
| 2.1.4 Seguridad y acceso | Login, `login_required`, CSRF, BPass, separación de pedidos por usuario y permisos API | Cumplido técnicamente |
| 3.1.1 Django REST Framework | `REST_FRAMEWORK`, serializers, routers y viewsets configurados | Cumplido |
| 3.1.2 Autenticación JWT | `/api/token/`, `/api/token/refresh/` y permisos autenticados | Cumplido |
| 3.1.3 Respuestas JSON | Endpoints de productos y pedidos mediante serializers DRF | Cumplido |
| 3.1.4 API RESTful funcional | Routers, métodos HTTP, CRUD de productos y consulta protegida de pedidos | Cumplido técnicamente |

## Entregables de diseño

- [Flujo principal](flujo.md)
- [Modelo entidad-relación](modelo-datos.md)
- Las plantillas en `musicpro/templates/` constituyen el prototipo navegable de las vistas.

La validación académica del alcance, la investigación de soluciones similares, la presentación y la demostración deben ser realizadas por el estudiante con el docente.
