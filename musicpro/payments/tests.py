from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import BeatPayWallet


User = get_user_model()


class CardSecurityActionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='card_owner', password='CardOwner!2026')
        self.wallet = BeatPayWallet.objects.create(
            user=self.user,
            numero_tarjeta='4111111111111111',
            token='card-test-token',
        )
        self.client.force_login(self.user)

    def test_get_cannot_change_card_state(self):
        response = self.client.get(reverse('payments:bloquear'))

        self.wallet.refresh_from_db()
        self.assertEqual(response.status_code, 405)
        self.assertEqual(self.wallet.estado, 'activa')

    def test_post_blocks_and_reactivates_card(self):
        block_response = self.client.post(reverse('payments:bloquear'), {'accion': 'bloquear'})
        self.wallet.refresh_from_db()
        self.assertEqual(block_response.status_code, 302)
        self.assertEqual(self.wallet.estado, 'bloqueada')

        enable_response = self.client.post(reverse('payments:bloquear'), {'accion': 'habilitar'})
        self.wallet.refresh_from_db()
        self.assertEqual(enable_response.status_code, 302)
        self.assertEqual(self.wallet.estado, 'activa')