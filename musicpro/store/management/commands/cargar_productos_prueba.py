from django.core.management.base import BaseCommand, CommandError
from faker import Faker

from store.models import Category, Product

PRODUCTOS_MUSICALES = [
    ('Yamaha Pacifica 112V', 'Instrumentos', 'Sala de guitarras', 400000, 500000, 'Guitarra eléctrica HSS de seis cuerdas.'),
    ('Fender Player II Stratocaster', 'Instrumentos', 'Sala de guitarras', 1200000, 1450000, 'Guitarra eléctrica Stratocaster de la serie Player II.'),
    ("Squier Classic Vibe '60s Stratocaster", 'Instrumentos', 'Sala de guitarras', 600000, 750000, 'Guitarra eléctrica inspirada en una Stratocaster de los años sesenta.'),
    ('Yamaha PSR-E383', 'Instrumentos', 'Sala de teclados', 260000, 330000, 'Teclado portátil Yamaha de 61 teclas.'),
    ('Casio CT-S300', 'Instrumentos', 'Sala de teclados', 190000, 260000, 'Teclado portátil Casiotone de 61 teclas.'),
    ('Yamaha DTX402K', 'Instrumentos', 'Sala de baterías', 600000, 760000, 'Batería electrónica de la serie Yamaha DTX402.'),
    ('Pearl Roadshow RS505C', 'Instrumentos', 'Sala de baterías', 800000, 980000, 'Batería acústica Pearl Roadshow de cinco piezas.'),
    ('JBL Charge 5', 'Audio', 'Sala de audio', 170000, 230000, 'Parlante Bluetooth portátil JBL resistente al agua.'),
    ('Shure SM58', 'Audio', 'Sala de audio', 110000, 150000, 'Micrófono dinámico cardioide Shure para voces.'),
    ('Audio-Technica ATH-M50x', 'Audio', 'Sala de audio', 150000, 210000, 'Audífonos de monitoreo profesional Audio-Technica.'),
    ('BOSS DS-1 Distortion', 'Accesorios', 'Bodega de pedales', 80000, 120000, 'Pedal BOSS de distorsión para guitarra eléctrica.'),
    ("D'Addario EXL110", 'Accesorios', 'Bodega de cuerdas', 7000, 13000, 'Juego de cuerdas D\'Addario XL Nickel Wound calibre 10-46.'),
]

UBICACIONES_POR_CATEGORIA = {
    'Instrumentos': ['Sala de guitarras', 'Sala de teclados', 'Sala de baterías'],
    'Audio': ['Estudio de audio', 'Estantería de audio'],
    'Accesorios': ['Bodega de accesorios', 'Pasillo de pedales y cuerdas'],
}


class Command(BaseCommand):
    help = 'Genera productos de prueba basados en modelos musicales reales.'

    def add_arguments(self, parser):
        parser.add_argument('--total', type=int, required=True)

    def handle(self, *args, **options):
        total = options['total']
        if total < 1:
            raise CommandError('--total debe ser mayor que cero.')

        fake = Faker('es_CL')
        fake.seed_instance(42)
        categorias = {
            nombre: Category.objects.get_or_create(name=nombre)[0]
            for nombre in ('Instrumentos', 'Audio', 'Accesorios')
        }
        creados = 0
        actualizados = 0

        for numero in range(total):
            nombre, categoria, ubicacion, precio_minimo, precio_maximo, descripcion = fake.random_element(
                elements=PRODUCTOS_MUSICALES
            )
            _, creado = Product.objects.update_or_create(
                codigo=f'TEST-{numero + 1:06d}',
                defaults={
                    'nombre': nombre,
                    'categoria': categorias[categoria],
                    'precio': fake.random_int(min=precio_minimo, max=precio_maximo),
                    'descripcion': descripcion,
                    'stock': fake.random_int(min=1, max=20),
                    'ubicacion': ubicacion,
                },
            )
            if creado:
                creados += 1
            else:
                actualizados += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Seeder finalizado: {creados} productos creados y '
                f'{actualizados} actualizados.'
            )
        )