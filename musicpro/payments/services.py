"""Núcleo del sistema de pago BeatPay + antifraude + boucher + notificaciones."""
import uuid
from decimal import Decimal

from django.contrib.auth.models import User
from django.conf import settings
from django.db import transaction

from .models import BeatPayWallet, Transaction, Voucher
from fraud.models import FraudLog, FraudRule
from notifications.models import Notification


def obtener_wallet(user):
    """Crea la tarjeta virtual BeatPay si aún no existe."""
    wallet, _ = BeatPayWallet.objects.get_or_create(
        user=user,
        defaults={
            'numero_tarjeta': '4659-' + '-'.join(
                str(uuid.uuid4().int)[:4] for _ in range(3)
            ),
            'token': uuid.uuid4().hex,
        },
    )
    return wallet


def _proximo_folio():
    ultimo = Transaction.objects.order_by('-folio').first()
    return (ultimo.folio + 1) if ultimo else 1000


def _revisar_antifraude(user, monto):
    """Valida reglas de riesgo. Retorna un FraudLog si sospecha, o None."""
    umbral = 0
    regla = FraudRule.objects.filter(activa=True).order_by('-umbral_monto').first()
    if regla:
        umbral = regla.umbral_monto

    if float(monto) > float(umbral) and float(umbral) > 0:
        log = FraudLog.objects.create(
            user=user,
            tipo='monto_inusual',
            detalle=f'Monto {monto} supera el umbral de {umbral}',
            monto=monto,
        )
        return log
    return None


def procesar_pago(user, monto, concepto='', tipo='compra_cliente', referencia=''):
    """Procesa un pago desde la tarjeta virtual con validación de saldo y fraude.

    Retorna (resultado: str, transaction: Transaction|None, mensaje: str).
    """
    monto = Decimal(str(monto))
    with transaction.atomic():
        wallet = BeatPayWallet.objects.select_for_update().get(user=user)

        if wallet.estado == 'bloqueada':
            return 'rechazada', None, 'La tarjeta virtual está bloqueada (anti-robo).'

        fraude = _revisar_antifraude(user, monto)
        if fraude:
            Notification.objects.create(
                user=user,
                tipo='seguridad',
                mensaje=('Se detectó una operación sospechosa y fue bloqueada '
                         'preventivamente: ' + fraude.detalle),
            )
            return 'rechazada', None, 'Operación bloqueada por el sistema antifraude.'

        if wallet.saldo < monto:
            folio = _proximo_folio()
            txn = Transaction.objects.create(
                wallet=wallet, monto=monto, concepto=concepto, tipo=tipo,
                resultado='rechazada_saldo', folio=folio, referencia=referencia,
            )
            voucher = txn.guardar_voucher()
            Notification.objects.create(
                user=user,
                tipo='pago_rechazado',
                mensaje=(f'No pudimos procesar tu {concepto or "pago"} por '
                         f'{monto} CLP. Saldo insuficiente. Se entregó el '
                         f'comprobante de rechazo folio {voucher.folio}.'),
                voucher=voucher,
            )
            return 'rechazada', txn, 'Saldo insuficiente para realizar la operación.'

        wallet.debitar(monto)
        folio = _proximo_folio()
        txn = Transaction.objects.create(
            wallet=wallet, monto=monto, concepto=concepto, tipo=tipo,
            resultado='aprobada', folio=folio, referencia=referencia,
        )
        voucher = txn.guardar_voucher()
        Notification.objects.create(
            user=user,
            tipo='pago_ok',
            mensaje=(f'Pago aprobado: {monto} CLP por {concepto or "compra"}. '
                     f'Comprobante folio {voucher.folio}.'),
            voucher=voucher,
        )
        return 'aprobada', txn, f'Pago aprobado. Comprobante folio {voucher.folio}.'


def recargar_saldo(user, monto):
    """Recarga saldo en la tarjeta virtual."""
    monto = Decimal(str(monto))
    wallet = obtener_wallet(user)
    wallet.cargar_saldo(monto)
    folio = _proximo_folio()
    txn = Transaction.objects.create(
        wallet=wallet,
        monto=monto,
        concepto='Recarga de saldo BeatPay',
        tipo='recarga',
        resultado='aprobada',
        folio=folio,
    )
    voucher = txn.guardar_voucher()
    Notification.objects.create(
        user=user,
        tipo='pago_ok',
        mensaje=f'Recarga exitosa de {monto} CLP. Comprobante folio {voucher.folio}.',
        voucher=voucher,
    )
    return txn
