from django.contrib.auth.models import User
from django.db.models import Q
from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify

from users.models import Profile


class RegistrationTests(TestCase):
    def registration_data(self, email):
        return {
            'username': 'registro_demo',
            'email': email,
            'rut': '12.345.678-5',
            'telefono': '+56912345678',
            'pais': 'CL',
            'password': 'ClaveSegura123!',
            'password2': 'ClaveSegura123!',
            'bpass': '123456',
            'bpass2': '123456',
        }

    def test_registration_rejects_missing_email(self):
        response = self.client.post(reverse('users:registro'), self.registration_data(''))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='registro_demo').exists())

    def test_registration_saves_normalized_email(self):
        response = self.client.post(
            reverse('users:registro'),
            self.registration_data('  Ana.Soto@example.com  '),
        )

        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='registro_demo')
        self.assertEqual(user.email, 'ana.soto@example.com')
        self.assertEqual(user.profile.rol, 'cliente')


class LoginRoleRedirectTests(TestCase):
    def test_operator_login_redirects_to_custom_panel(self):
        operator = User.objects.create_user(
            username='operator_login',
            password='Operador!2026Seguro',
            is_staff=True,
        )
        operator.profile.rol = 'operador'
        operator.profile.save(update_fields=['rol'])

        response = self.client.post(reverse('users:login'), {
            'username': operator.username,
            'password': 'Operador!2026Seguro',
        })

        self.assertRedirects(response, reverse('backoffice:dashboard'))


class GeneratedClientDataTests(TestCase):
    def clientes_generados(self):
        return User.objects.filter(
            Q(username__startswith='cliente_test_')
            | Q(email__endswith='@example.com')
            | Q(email__endswith='@example.net')
            | Q(email__endswith='@example.org')
        )

    def test_seed_is_repeatable_and_creates_valid_customer_data(self):
        from django.core.management import call_command

        call_command('cargar_clientes_prueba', total=2)
        first_run = list(self.clientes_generados().order_by('id'))
        call_command('cargar_clientes_prueba', total=2)
        second_run = list(self.clientes_generados().order_by('id'))

        self.assertEqual(len(second_run), 2)
        self.assertEqual(
            [(user.first_name, user.last_name, user.email) for user in first_run],
            [(user.first_name, user.last_name, user.email) for user in second_run],
        )
        for user in second_run:
            expected_username = f'{slugify(user.first_name)}_{slugify(user.last_name)}'
            self.assertTrue(user.username.startswith(expected_username))
            self.assertNotIn('cliente_test', user.username)
            self.assertRegex(user.email, r'@example\.(com|net|org)$')
            self.assertTrue(Profile.objects.filter(user=user, pais='CL', moneda='CLP').exists())

    def test_command_updates_existing_demo_user(self):
        user = User.objects.create_user(
            username='cliente_test_antiguo',
            email='cliente-antiguo@example.test',
        )
        user.profile.rut = '12.345.678-5'
        user.profile.telefono = '+56912345678'
        user.profile.save()

        from django.core.management import call_command
        call_command('cargar_clientes_prueba', total=1)

        user.refresh_from_db()
        self.assertNotIn('cliente_test', user.username)
        self.assertTrue(user.email.endswith(('@example.com', '@example.net', '@example.org')))
        self.assertTrue(user.first_name)
        self.assertTrue(user.last_name)
        self.assertTrue(User.objects.filter(pk=user.pk).exists())
        self.assertRegex(user.profile.telefono, r'^\+569\d{8}$')
        self.assertRegex(user.profile.rut, r'^\d{7,8}-[0-9K]$')