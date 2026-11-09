from io import StringIO
from itertools import cycle
import re

from django.contrib.auth.models import User
from django.core.management import call_command
from django.db.models import Q
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from rest_framework.test import APIClient

from .models import CartItem, Product
from .management.commands.cargar_productos_prueba import PRODUCTOS_MUSICALES
from users.models import Profile


class StoreApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='api_test_user',
            password='ApiTestPassword123!',
        )
        self.client = APIClient()

    def test_jwt_allows_access_to_orders(self):
        response = self.client.post(
            '/api/token/',
            {'username': 'api_test_user', 'password': 'ApiTestPassword123!'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        orders_response = self.client.get('/api/pedidos/')
        self.assertEqual(orders_response.status_code, 200)
        self.assertEqual(orders_response.data, [])

    def test_product_api_only_returns_active_products(self):
        Product.objects.create(
            nombre='Producto API activo',
            codigo='API-ACTIVE',
            precio='1000',
            stock=2,
        )
        Product.objects.create(
            nombre='Producto API inactivo',
            codigo='API-INACTIVE',
            precio='2000',
            stock=1,
            estado='inactivo',
        )

        response = self.client.get('/api/productos/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item['codigo'] for item in response.data], ['API-ACTIVE'])


class CartMutationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cart_user', password='CartTestPassword123!')
        self.product = Product.objects.create(
            nombre='Producto carrito',
            codigo='CART-1',
            precio='5000',
            stock=3,
        )
        self.client.force_login(self.user)

    def test_add_to_cart_requires_post(self):
        response = self.client.get(reverse('store:agregar', args=[self.product.pk]))

        self.assertEqual(response.status_code, 405)
        self.assertFalse(CartItem.objects.exists())

    def test_add_to_cart_post_has_csrf_protection_and_adds_active_product(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        page = client.get(reverse('store:inicio'))
        csrf_token = client.cookies['csrftoken'].value
        response = client.post(
            reverse('store:agregar', args=[self.product.pk]),
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(page.status_code, 200)
        self.assertContains(page, 'name="csrfmiddlewaretoken"')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CartItem.objects.get(cart__user=self.user, product=self.product).cantidad, 1)

    def test_inactive_product_cannot_be_added_to_cart(self):
        self.product.estado = 'inactivo'
        self.product.save(update_fields=['estado'])

        response = self.client.post(reverse('store:agregar', args=[self.product.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(CartItem.objects.exists())

    def test_catalog_does_not_show_inactive_products(self):
        self.product.estado = 'inactivo'
        self.product.save(update_fields=['estado'])

        response = self.client.get(reverse('store:inicio'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.product.nombre)


class ProductDataCommandTests(TestCase):
    def test_command_reaches_total_without_duplicating_existing_rows(self):
        output = StringIO()
        call_command('cargar_productos_prueba', total=5, stdout=output)
        call_command('cargar_productos_prueba', total=5, stdout=output)

        self.assertEqual(Product.objects.filter(codigo__startswith='TEST-').count(), 5)
        allowed_names = {producto[0] for producto in PRODUCTOS_MUSICALES}
        self.assertTrue(
            all(name in allowed_names for name in Product.objects.filter(codigo__startswith='TEST-').values_list('nombre', flat=True))
        )


class ClientDataCommandTests(TestCase):
    def test_generates_valid_unique_rut_and_mobile_phone(self):
        call_command('cargar_clientes_prueba', total=3)
        call_command('cargar_clientes_prueba', total=3)
        profiles = list(Profile.objects.filter(
            Q(user__email__endswith='@example.com')
            | Q(user__email__endswith='@example.net')
            | Q(user__email__endswith='@example.org')
        ))

        self.assertEqual(len(profiles), 3)
        self.assertEqual(len({profile.rut for profile in profiles}), 3)
        for profile in profiles:
            self.assertRegex(profile.rut, r'^\d{7,8}-[0-9K]$')
            self.assertRegex(profile.telefono, r'^\+569\d{8}$')
            body, verifier = profile.rut.replace('.', '').split('-')
            total = sum(int(digit) * factor for digit, factor in zip(body[::-1], cycle(range(2, 8))))
            value = 11 - total % 11
            expected = '0' if value == 11 else 'K' if value == 10 else str(value)
            self.assertEqual(verifier, expected)
