from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from store.models import Category, Order, OrderItem, Product


User = get_user_model()


class BackofficeAccessTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username='panel_admin',
            password='M4sicPro!Panel-2026',
            is_staff=True,
        )
        self.staff.profile.rol = 'admin'
        self.staff.profile.save(update_fields=['rol'])

    def test_anonymous_user_is_redirected_from_panel(self):
        response = self.client.get(reverse('backoffice:dashboard'))

        self.assertRedirects(
            response,
            f"{reverse('users:login')}?next={reverse('backoffice:dashboard')}",
        )

    def test_authenticated_non_staff_user_is_forbidden(self):
        customer = User.objects.create_user(username='cliente', password='UnaClave!2026')
        self.client.force_login(customer)

        response = self.client.get(reverse('backoffice:dashboard'))

        self.assertEqual(response.status_code, 403)

    def test_operator_can_manage_catalog_but_not_users_or_deletions(self):
        operator = User.objects.create_user(
            username='panel_operador',
            password='Operador!2026Seguro',
            is_staff=True,
        )
        operator.profile.rol = 'operador'
        operator.profile.save(update_fields=['rol'])
        product = Product.objects.create(
            nombre='Producto de operador',
            codigo='OP-1',
            precio=Decimal('3000'),
            stock=2,
        )
        self.client.force_login(operator)

        self.assertEqual(self.client.get(reverse('backoffice:products')).status_code, 200)
        self.assertEqual(self.client.get(reverse('backoffice:product_edit', args=[product.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse('backoffice:orders')).status_code, 200)
        self.assertEqual(self.client.get(reverse('backoffice:reports')).status_code, 200)
        self.assertEqual(self.client.get(reverse('backoffice:users')).status_code, 403)
        self.assertEqual(self.client.get(reverse('backoffice:categories')).status_code, 403)
        self.assertEqual(self.client.get(reverse('backoffice:product_delete', args=[product.pk])).status_code, 403)

    def test_staff_can_open_admin_pages(self):
        self.client.force_login(self.staff)
        product = Product.objects.create(
            nombre='Producto de navegación',
            codigo='NAV-1',
            precio=Decimal('5000'),
            stock=3,
        )
        category = Category.objects.create(name='Categoría de navegación')
        customer = User.objects.create_user(username='cliente_nav', password='Cliente!2026Seguro')
        order = Order.objects.create(user=customer, estado='pendiente')
        routes = (
            'backoffice:dashboard',
            'backoffice:products',
            ('backoffice:product_create', ()),
            ('backoffice:product_edit', (product.pk,)),
            'backoffice:categories',
            'backoffice:category_create',
            ('backoffice:category_edit', (category.pk,)),
            'backoffice:users',
            ('backoffice:user_create', ()),
            ('backoffice:user_edit', (customer.pk,)),
            'backoffice:orders',
            'backoffice:order_create',
            ('backoffice:order_edit', (order.pk,)),
            'backoffice:reports',
        )

        for route_spec in routes:
            route, args = route_spec if isinstance(route_spec, tuple) else (route_spec, ())
            with self.subTest(route=route):
                self.assertEqual(self.client.get(reverse(route, args=args)).status_code, 200)

    def test_logout_requires_post_and_clears_session(self):
        self.client.force_login(self.staff)

        get_response = self.client.get(reverse('users:logout'))
        post_response = self.client.post(reverse('users:logout'))

        self.assertEqual(get_response.status_code, 405)
        self.assertEqual(post_response.status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)


class BackofficeCrudTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username='catalog_admin',
            password='M4sicPro!Panel-2026',
            is_staff=True,
        )
        self.staff.profile.rol = 'admin'
        self.staff.profile.save(update_fields=['rol'])
        self.customer = User.objects.create_user(username='cliente_tienda', password='Cliente!2026Seguro')
        self.category = Category.objects.create(name='Instrumentos')
        self.client.force_login(self.staff)

    def test_product_create_uses_posted_values(self):
        response = self.client.post(reverse('backoffice:product_create'), {
            'nombre': 'Teclado de prueba',
            'codigo': 'TEST-KEY-1',
            'categoria': str(self.category.pk),
            'precio': '45990',
            'stock': '7',
            'estado': 'activo',
            'ubicacion': 'Bodega A',
            'descripcion': 'Producto de prueba',
        })

        product = Product.objects.get(codigo='TEST-KEY-1')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(product.categoria, self.category)
        self.assertEqual(product.precio, Decimal('45990'))
        self.assertEqual(product.stock, 7)
        self.assertEqual(product.estado, 'activo')

    def test_user_create_saves_profile_and_hashed_password(self):
        response = self.client.post(reverse('backoffice:user_create'), {
            'username': 'cliente_nuevo',
            'email': 'nuevo@example.com',
            'first_name': 'Cliente',
            'last_name': 'Nuevo',
            'rut': '12345678-5',
            'telefono': '+56912345678',
            'rol': 'cliente',
            'password': 'K9!vQ4#pL2xZ7mR8',
            'is_active': 'on',
        })

        created_user = User.objects.get(username='cliente_nuevo')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(created_user.check_password('K9!vQ4#pL2xZ7mR8'))
        self.assertEqual(created_user.profile.rut, '12345678-5')
        self.assertFalse(created_user.is_staff)

    def test_user_create_can_assign_operator_role(self):
        response = self.client.post(reverse('backoffice:user_create'), {
            'username': 'operador_nuevo',
            'email': 'operador@example.com',
            'rol': 'operador',
            'password': 'Op3rador!Seguro2026',
            'is_staff': 'on',
            'is_active': 'on',
        })

        operator = User.objects.get(username='operador_nuevo')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(operator.is_staff)
        self.assertEqual(operator.profile.rol, 'operador')

    def test_product_with_sales_cannot_be_deleted(self):
        product = Product.objects.create(
            nombre='Producto vendido',
            codigo='SOLD-1',
            precio=Decimal('1000'),
            stock=1,
        )
        order = Order.objects.create(user=self.customer, total=Decimal('1000'), estado='pagada')
        OrderItem.objects.create(
            order=order,
            product=product,
            cantidad=1,
            precio_unitario=Decimal('1000'),
        )

        response = self.client.post(reverse('backoffice:product_delete', args=[product.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Product.objects.filter(pk=product.pk).exists())
        self.assertTrue(OrderItem.objects.filter(order=order, product=product).exists())

    def test_reports_show_store_queries(self):
        Product.objects.create(
            nombre='Reporte teclado',
            codigo='REPORT-1',
            precio=Decimal('12000'),
            stock=4,
            categoria=self.category,
        )

        response = self.client.get(reverse('backoffice:reports'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Productos por categoría')
        self.assertContains(response, 'Monto vendido en un día')
        self.assertContains(response, 'Reporte teclado')

    def test_create_order_as_pending_without_payment_transaction(self):
        product = Product.objects.create(
            nombre='Venta manual',
            codigo='MANUAL-1',
            precio=Decimal('12000'),
            stock=5,
        )

        response = self.client.post(reverse('backoffice:order_create'), {
            'cliente': str(self.customer.pk),
            'productos': [str(product.pk), ''],
            'cantidades': ['2', ''],
        })

        order = Order.objects.get(user=self.customer)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(order.estado, 'pendiente')
        self.assertIsNone(order.transaction_id)
        self.assertEqual(order.total, Decimal('24000'))
        self.assertEqual(order.order_items.get().cantidad, 2)

    def test_unpaid_order_cannot_be_marked_as_paid(self):
        order = Order.objects.create(user=self.customer, estado='pendiente')

        response = self.client.post(reverse('backoffice:order_status', args=[order.pk]), {
            'estado': 'pagada',
        })

        order.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(order.estado, 'pendiente')

    def test_pending_order_can_be_deleted(self):
        order = Order.objects.create(user=self.customer, estado='pendiente')

        response = self.client.post(reverse('backoffice:order_delete', args=[order.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Order.objects.filter(pk=order.pk).exists())

    def test_invalid_product_identifier_does_not_create_order(self):
        response = self.client.post(reverse('backoffice:order_create'), {
            'cliente': str(self.customer.pk),
            'productos': ['invalid'],
            'cantidades': ['1'],
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Order.objects.exists())
        self.assertContains(response, 'Selecciona un producto válido')

    def test_category_and_price_report_filters(self):
        Product.objects.create(
            nombre='Guitarra rango',
            codigo='RANGE-1',
            precio=Decimal('12000'),
            stock=6,
            categoria=self.category,
        )
        Product.objects.create(
            nombre='Bajo fuera de rango',
            codigo='RANGE-2',
            precio=Decimal('40000'),
            stock=2,
        )

        response = self.client.get(reverse('backoffice:reports'), {
            'categoria': str(self.category.pk),
            'precio_min': '10000',
            'precio_max': '15000',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['category_products'].count(), 1)
        self.assertEqual(response.context['price_products'].count(), 1)

    def test_daily_sales_report_sums_only_paid_orders(self):
        Order.objects.create(user=self.customer, total=Decimal('12345'), estado='pagada')
        Order.objects.create(user=self.customer, total=Decimal('9000'), estado='pendiente')
        today = timezone.localdate().isoformat()

        response = self.client.get(reverse('backoffice:reports'), {
            'desde': today,
            'hasta': today,
            'dia': today,
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['period_count'], 1)
        self.assertEqual(response.context['day_total'], Decimal('12345'))