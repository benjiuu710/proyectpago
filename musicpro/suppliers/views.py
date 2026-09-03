from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Supplier, SupplierOrder, SupplierOrderItem
from payments.services import procesar_pago, obtener_wallet
from notifications.models import Notification


def _es_encargado(user):
    return user.is_authenticated and user.profile.rol in ('admin', 'encargado')


@login_required
def listar_proveedores(request):
    proveedores = Supplier.objects.filter(activo=True)
    return render(request, 'suppliers/proveedores.html', {'proveedores': proveedores})


@login_required
def detalle_proveedor(request, pk):
    proveedor = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        # Construir orden de compra con los productos marcados
        orden = SupplierOrder.objects.create(supplier=proveedor)
        total = 0
        for item in proveedor.catalog.all():
            cant = int(request.POST.get(f'cant_{item.pk}', 0))
            if cant > 0:
                SupplierOrderItem.objects.create(
                    order=orden, product=item.product, cantidad=cant,
                    precio_unitario=item.precio_mayorista,
                )
                total += item.precio_mayorista * cant
        orden.recalcular()

        if total <= 0:
            orden.delete()
            messages.error(request, 'Selecciona al menos un producto con cantidad > 0.')
            return redirect('suppliers:detalle', pk=pk)

        # Validación de fondos automática
        resultado, txn, msg = procesar_pago(
            request.user, total,
            concepto=f'Compra a proveedor {proveedor.nombre}',
            tipo='pago_proveedor',
            referencia=f'SUP-{orden.pk}',
        )

        if resultado == 'aprobada':
            orden.estado = 'pagada'
            orden.save(update_fields=['estado'])
            # Reponer stock
            for item in orden.items.all():
                item.product.stock += item.cantidad
                item.product.save(update_fields=['stock'])
            messages.success(request, f'Compra a proveedor aprobada. {msg}')
        else:
            orden.estado = 'rechazada'
            orden.observacion = msg
            orden.save(update_fields=['estado', 'observacion'])
            messages.error(request, f'Compra rechazada: {msg}')
        return redirect('suppliers:ordenes')

    return render(request, 'suppliers/detalle.html', {'proveedor': proveedor})


@login_required
def lista_ordenes(request):
    ordenes = SupplierOrder.objects.order_by('-creada')
    return render(request, 'suppliers/ordenes.html', {'ordenes': ordenes})
