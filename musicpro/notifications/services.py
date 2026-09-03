"""Bot de atención 24/7 para consultas de saldo, pedidos, puntos y seguridad."""
import re

from .models import ChatMessage, Notification
from payments.models import BeatPayWallet
from store.models import Order
from loyalty.models import PointsWallet


def _normalizar(texto):
    return texto.lower().strip()


def _responder_saldo(user):
    wallet = BeatPayWallet.objects.filter(user=user).first()
    if wallet:
        return (f'Tu saldo en la tarjeta BeatPay es de {wallet.saldo} CLP. '
                f'Estado de la tarjeta: {wallet.get_estado_display()} ({wallet.estado}).')
    return 'Aún no tienes tarjeta BeatPay creada.'


def _responder_pedido(user, texto):
    m = re.search(r'(\d+)', texto)
    if m:
        try:
            orden = Order.objects.get(pk=int(m.group(1)), user=user)
            return f'Tu pedido #{orden.pk} está en estado: {orden.get_estado_display()}. Total: {orden.total} CLP.'
        except Order.DoesNotExist:
            return 'No encontré un pedido tuyo con ese número.'
    return ('Para revisar el estado de tu pedido, dime el número (ej: "mi pedido 12"). '
            'Tus pedidos: ' + ', '.join(f'#{o.pk}' for o in Order.objects.filter(user=user)) or 'no tienes pedidos aún.')


def _responder_puntos(user):
    pw = PointsWallet.objects.filter(user=user).first()
    if pw:
        return f'Tienes {pw.puntos} puntos disponibles en tu programa de fidelización.'
    return 'Aún no tienes puntos acumulados.'


def _bloquear_tarjeta(user):
    wallet = BeatPayWallet.objects.filter(user=user).first()
    if wallet:
        wallet.bloquear()
        Notification.objects.create(
            user=user, tipo='seguridad',
            mensaje='Tu tarjeta virtual fue bloqueada por solicitud del bot (anti-robo).',
        )
        return 'Tu tarjeta virtual ha sido BLOQUEADA preventivamente. Puedes pedir que la habiliten desde el panel.'
    return 'No tienes tarjeta BeatPay creada.'


def responder_bot(user, texto):
    """Devuelve la respuesta del bot y guarda el par de mensajes."""
    ChatMessage.objects.create(user=user, remitente='usuario', texto=texto)
    t = _normalizar(texto)

    if re.search(r'saldo|cu[aá]nto (tengo|dinero)|presupuesto', t):
        respuesta = '💰 ' + _responder_saldo(user)
    elif re.search(r'pedido|orden|compra.*(estado|seguimiento)|estado.*(pedido|compra|orden)', t):
        respuesta = _responder_pedido(user, texto)
    elif re.search(r'punto|fidelizaci|recompensa|canjear', t):
        respuesta = '⭐ ' + _responder_puntos(user)
    elif re.search(r'bloquear|bloqueo|robo|p[eé]rdida|emergencia|congelar', t):
        respuesta = _bloquear_tarjeta(user)
    elif re.search(r'hola|buenas|saludos', t):
        respuesta = ('¡Hola! Soy el asistente MusicPro 24/7. Puedo ayudarte con tu '
                     'saldo, el estado de un pedido, tus puntos o bloquear tu tarjeta '
                     'por emergencia.')
    elif re.search(r'comprobante|boucher|voucher', t):
        respuesta = ('Tus comprobantes se generan automáticamente tras cada operación. '
                     'Revisa tu bandeja de notificaciones.')
    else:
        respuesta = ('Puedo ayudarte con: saldo, estado de pedido (#), puntos y '
                     'bloqueo de tarjeta por robo/emergencia. ¿Qué necesitas?')

    ChatMessage.objects.create(user=user, remitente='bot', texto=respuesta)
    return respuesta
