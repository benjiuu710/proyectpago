from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from payments.models import BeatPayWallet


User = get_user_model()


class AccountSecurityActionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='fraud_owner', password='FraudOwner!2026')
        self.wallet = BeatPayWallet.objects.create(
            user=self.user,
            numero_tarjeta='5222222222222222',
            token='fraud-test-token',
        )
        self.client.force_login(self.user)

    def test_get_cannot_block_account_or_card(self):
        response = self.client.get(reverse('fraud:bloquear_cuenta'))

        self.user.profile.refresh_from_db()
        self.wallet.refresh_from_db()
        self.assertEqual(response.status_code, 405)
        self.assertEqual(self.user.profile.estado, 'activa')
        self.assertEqual(self.wallet.estado, 'activa')

    def test_post_blocks_account_and_card(self):
        response = self.client.post(reverse('fraud:bloquear_cuenta'))

        self.user.profile.refresh_from_db()
        self.wallet.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.profile.estado, 'bloqueada')
        self.assertEqual(self.wallet.estado, 'bloqueada')