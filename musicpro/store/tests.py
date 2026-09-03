from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient


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
