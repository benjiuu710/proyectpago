from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.utils.text import slugify
from faker import Faker

from users.models import Profile


USERNAME_PREFIX = 'cliente_test_'


def generar_rut(numero):
    suma = 0
    multiplicador = 2
    for digito in reversed(str(numero)):
        suma += int(digito) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1

    verificador = 11 - suma % 11
    if verificador == 11:
        verificador = '0'
    elif verificador == 10:
        verificador = 'K'
    else:
        verificador = str(verificador)

    return f'{numero}-{verificador}'


class Command(BaseCommand):
    help = 'Genera perfiles de clientes chilenos ficticios con Faker.'

    def add_arguments(self, parser):
        parser.add_argument('--total', type=int, required=True)

    def handle(self, *args, **options):
        total = options['total']
        if total < 1:
            raise CommandError('--total debe ser mayor que cero.')

        fake = Faker('es_CL')
        fake.seed_instance(42)
        clientes_existentes = User.objects.filter(
            Q(username__startswith=USERNAME_PREFIX)
            | Q(email__endswith='@example.com')
            | Q(email__endswith='@example.net')
            | Q(email__endswith='@example.org')
        ).order_by('id').iterator()
        creados = 0
        actualizados = 0

        for numero in range(total):
            rut_base = fake.unique.random_int(min=10_000_000, max=25_000_000)
            rut = generar_rut(rut_base)
            nombre = fake.first_name()
            apellido = fake.last_name()
            email = fake.unique.safe_email()
            telefono = fake.numerify(text='+569########')

            user = next(clientes_existentes, None)
            if user is None:
                user = User()
                user.set_unusable_password()
                creados += 1
            else:
                actualizados += 1

            nombre_usuario = f'{slugify(nombre)}_{slugify(apellido)}'
            username = nombre_usuario
            sufijo = numero + 1
            while User.objects.filter(username=username).exclude(pk=user.pk).exists():
                username = f'{nombre_usuario}_{sufijo:03d}'
                sufijo += 1

            user.username = username
            user.first_name = nombre
            user.last_name = apellido
            user.email = email
            user.save()

            profile, _ = Profile.objects.get_or_create(user=user)
            profile.rut = rut
            profile.telefono = telefono
            profile.pais = 'CL'
            profile.moneda = 'CLP'
            profile.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'Seeder finalizado: {creados} clientes creados y '
                f'{actualizados} actualizados.'
            )
        )