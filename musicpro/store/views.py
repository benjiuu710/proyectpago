from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.db import transaction
from .models import Product, Cart, CartItem, Order, OrderItem
from loyalty.models import PointsWallet, PointsLedger
from payments.services import procesar_pago, obtener_wallet


def inicio(request):
    if not request.user.is_authenticated:
        return render(request, 'store/bienvenida.html')
    productos = Product.objects.all()
    categoria = request.GET.get('categoria')
    busqueda = request.GET.get('q')
    if categoria:
        productos = productos.filter(categoria__id=categoria)
    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda)
    return render(request, 'store/inicio.html', {
        'productos': productos,
        'carrito_total': _contar_carrito(request),
    })


def _contar_carrito(request):
    if not request.user.is_authenticated:
        return 0
    cart = Cart.objects.filter(user=request.user).first()
    return sum(i.cantidad for i in cart.items.all()) if cart else 0


@login_required
def agregar_al_carrito(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item = CartItem.objects.filter(cart=cart, product=product).first()
    cantidad_actual = item.cantidad if item else 0
    if cantidad_actual >= product.stock:
        messages.error(request, 'No hay stock disponible para agregar más unidades.')
        return redirect('store:inicio')
    item, creado = CartItem.objects.get_or_create(cart=cart, product=product,
                                                  defaults={'cantidad': 1})
    if not creado:
        item.cantidad += 1
        item.save()
    messages.success(request, f'{product.nombre} añadido al carrito.')
    return redirect('store:inicio')


@login_required
def carrito(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    puntos = 0
    if hasattr(request.user, 'points_wallet'):
        puntos = request.user.points_wallet.puntos
    return render(request, 'store/carrito.html', {
        'cart': cart,
        'carrito_total': _contar_carrito(request),
        'puntos_disponibles': puntos,
    })


@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    wallet = obtener_wallet(request.user)

    if not cart or not cart.items.exists():
        messages.info(request, 'Tu carrito está vacío.')
        return redirect('store:carrito')

    if request.method == 'POST':
        bpass = request.POST.get('bpass', '')
        if not request.user.profile.bpass_hash or not check_password(bpass, request.user.profile.bpass_hash):
            messages.error(request, 'BPass incorrecto. La compra no fue procesada.')
            return redirect('store:checkout')
        usar_puntos = request.POST.get('usar_puntos') == 'on'
        for item in cart.items.select_related('product'):
            if item.cantidad > item.product.stock:
                messages.error(request, f'Stock insuficiente para {item.product.nombre}.')
                return redirect('store:carrito')
        total = cart.total()
        descuento = 0
        puntos_a_usar = 0
        pw = None

        # Aplicar punto si el usuario los usa
        if usar_puntos and hasattr(request.user, 'points_wallet'):
            pw = request.user.points_wallet
            # 1 punto = 10 CLP
            puntos_a_usar = min(pw.puntos, int(total / 10))
            descuento = puntos_a_usar * 10

        monto_final = total - descuento

        resultado, txn, msg = procesar_pago(
            request.user, monto_final,
            concepto='Compra en MusicPro',
            tipo='compra_cliente',
            referencia=f'ORDER-CART-{cart.pk}',
        )

        if resultado == 'aprobada':
            if pw and puntos_a_usar:
                pw.canjear(puntos_a_usar)
            orden = Order.objects.create(
                user=request.user,
                total=monto_final,
                estado='pagada',
                puntos_usados=puntos_a_usar if usar_puntos else 0,
                descuento_puntos=descuento,
                transaction=txn,
            )
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=orden, product=item.product,
                    cantidad=item.cantidad, precio_unitario=item.product.precio,
                )
                Product.objects.filter(pk=item.product_id).update(
                    stock=item.product.stock - item.cantidad,
                )
            # Acumular puntos (1 punto por cada 1000 CLP)
            puntos_ganados = int(monto_final / 1000)
            if puntos_ganados > 0:
                pw2 = PointsWallet.objects.get_or_create(user=request.user)[0]
                pw2.acumular(puntos_ganados)
                PointsLedger.objects.create(wallet=pw2, cantidad=puntos_ganados,
                                            motivo='Compra en tienda MusicPro')
            cart.items.all().delete()
            messages.success(request, f'¡Compra exitosa! {msg}')
            return redirect('store:orden', pk=orden.pk)

        messages.error(request, f'No se pudo procesar: {msg}')
        return redirect('store:carrito')

    return render(request, 'store/checkout.html', {
        'cart': cart,
        'total': cart.total(),
        'wallet': wallet,
        'carrito_total': _contar_carrito(request),
    })


@login_required
def orden_detalle(request, pk):
    orden = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'store/orden.html', {
        'orden': orden,
        'carrito_total': _contar_carrito(request),
    })
