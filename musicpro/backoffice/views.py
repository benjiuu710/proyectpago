from decimal import Decimal, InvalidOperation
from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date

from store.models import Category, Order, OrderItem, Product
from users.models import Profile


User = get_user_model()


def roles_required(*allowed_roles):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            profile = getattr(request.user, 'profile', None)
            if not request.user.is_staff or not (
                request.user.is_superuser
                or profile and profile.rol in allowed_roles
            ):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator


admin_required = roles_required('admin')
operator_required = roles_required('admin', 'operador')


@operator_required
def dashboard(request):
    return render(request, 'backoffice/dashboard.html', {
        'product_count': Product.objects.count(),
        'customer_count': User.objects.filter(is_staff=False, is_superuser=False).count(),
        'order_count': Order.objects.count(),
        'recent_orders': Order.objects.select_related('user').order_by('-creada')[:8],
    })


@operator_required
def product_list(request):
    products = Product.objects.select_related('categoria').order_by('nombre')
    search = request.GET.get('q', '').strip()
    if search:
        products = products.filter(Q(nombre__icontains=search) | Q(codigo__icontains=search))
    return render(request, 'backoffice/products.html', {
        'products': products,
        'search': search,
    })


@operator_required
def product_form(request, pk=None):
    product = get_object_or_404(Product, pk=pk) if pk else Product()
    categories = Category.objects.order_by('name')
    form_data = {
        'nombre': product.nombre,
        'codigo': product.codigo,
        'descripcion': product.descripcion,
        'precio': product.precio,
        'stock': product.stock,
        'estado': product.estado,
        'ubicacion': product.ubicacion,
        'categoria': product.categoria_id or '',
    }
    errors = []

    if request.method == 'POST':
        form_data = request.POST
        nombre = request.POST.get('nombre', '').strip()
        codigo = request.POST.get('codigo', '').strip()
        precio_text = request.POST.get('precio', '').strip()
        stock_text = request.POST.get('stock', '').strip()
        estado = request.POST.get('estado', '').strip()
        categoria_id = request.POST.get('categoria', '').strip()

        if not nombre:
            errors.append('El nombre es obligatorio.')
        if not codigo:
            errors.append('El código es obligatorio.')
        elif Product.objects.filter(codigo__iexact=codigo).exclude(pk=product.pk).exists():
            errors.append('Ya existe un producto con ese código.')
        if estado not in dict(Product.ESTADO_CHOICES):
            errors.append('Selecciona un estado válido para el producto.')

        try:
            precio = Decimal(precio_text)
            if not precio.is_finite() or precio < 0:
                raise InvalidOperation
        except (InvalidOperation, ValueError):
            precio = None
            errors.append('Ingresa un precio válido mayor o igual a cero.')

        try:
            stock = int(stock_text)
            if stock < 0:
                raise ValueError
        except ValueError:
            stock = None
            errors.append('El stock debe ser un número entero mayor o igual a cero.')

        categoria = None
        if categoria_id:
            categoria = Category.objects.filter(pk=categoria_id).first()
            if categoria is None:
                errors.append('Selecciona una categoría válida.')

        if not errors:
            product.nombre = nombre
            product.codigo = codigo
            product.descripcion = request.POST.get('descripcion', '').strip()
            product.precio = precio
            product.stock = stock
            product.estado = estado
            product.ubicacion = request.POST.get('ubicacion', '').strip()
            product.categoria = categoria
            if request.FILES.get('imagen'):
                product.imagen = request.FILES['imagen']
            product.save()
            messages.success(request, 'Producto guardado correctamente.')
            return redirect('backoffice:products')

    return render(request, 'backoffice/product_form.html', {
        'product': product if product.pk else None,
        'categories': categories,
        'estado_choices': Product.ESTADO_CHOICES,
        'form_data': form_data,
        'errors': errors,
    })


@admin_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        if OrderItem.objects.filter(product=product).exists():
            messages.error(request, 'No se puede eliminar un producto incluido en ventas; conserva su historial.')
        else:
            product.delete()
            messages.success(request, 'Producto eliminado correctamente.')
        return redirect('backoffice:products')
    return render(request, 'backoffice/confirm_delete.html', {
        'object': product,
        'cancel_url': 'backoffice:products',
        'heading': 'Eliminar producto',
    })


@admin_required
def category_list(request):
    return render(request, 'backoffice/categories.html', {
        'categories': Category.objects.order_by('name'),
    })


@admin_required
def category_form(request, pk=None):
    category = get_object_or_404(Category, pk=pk) if pk else Category()
    name = category.name
    error = ''
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            error = 'El nombre es obligatorio.'
        elif Category.objects.filter(name__iexact=name).exclude(pk=category.pk).exists():
            error = 'Ya existe una categoría con ese nombre.'
        else:
            category.name = name
            category.save()
            messages.success(request, 'Categoría guardada correctamente.')
            return redirect('backoffice:categories')
    return render(request, 'backoffice/category_form.html', {
        'category': category if category.pk else None,
        'name': name,
        'error': error,
    })


@admin_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Categoría eliminada. Los productos asociados quedaron sin categoría.')
        return redirect('backoffice:categories')
    return render(request, 'backoffice/confirm_delete.html', {
        'object': category,
        'cancel_url': 'backoffice:categories',
        'heading': 'Eliminar categoría',
    })


@admin_required
def user_list(request):
    users = User.objects.filter(is_superuser=False).select_related('profile').order_by('username')
    search = request.GET.get('q', '').strip()
    if search:
        users = users.filter(
            Q(username__icontains=search)
            | Q(email__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(profile__rut__icontains=search)
        )
    return render(request, 'backoffice/users.html', {
        'users': users,
        'search': search,
    })


@admin_required
def user_form(request, pk=None):
    user = get_object_or_404(User, pk=pk, is_superuser=False) if pk else User()
    profile = Profile.objects.filter(user=user).first() if user.pk else None
    form_data = {
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'rut': profile.rut if profile else '',
        'telefono': profile.telefono if profile else '',
        'rol': profile.rol if profile else 'cliente',
        'is_staff': user.is_staff,
        'is_active': user.is_active if user.pk else True,
    }
    errors = []

    if request.method == 'POST':
        form_data = request.POST
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        rut = request.POST.get('rut', '').strip()
        password = request.POST.get('password', '')
        is_staff = request.POST.get('is_staff') == 'on'
        is_active = request.POST.get('is_active') == 'on'

        if not username:
            errors.append('El nombre de usuario es obligatorio.')
        elif User.objects.filter(username__iexact=username).exclude(pk=user.pk).exists():
            errors.append('Ese nombre de usuario ya está registrado.')
        if email:
            try:
                validate_email(email)
            except ValidationError:
                errors.append('Ingresa un correo electrónico válido.')
        if rut:
            rut_matches = Profile.objects.filter(rut__iexact=rut)
            if user.pk:
                rut_matches = rut_matches.exclude(user=user)
            if rut_matches.exists():
                errors.append('Ese RUT ya está asociado a otro usuario.')
        if not user.pk and not password:
            errors.append('La contraseña es obligatoria para crear un usuario.')
        if password:
            try:
                validate_password(password, user=user)
            except ValidationError as error:
                errors.extend(error.messages)
        if user.pk == request.user.pk and (not is_active or not is_staff):
            errors.append('No puedes desactivar ni quitar el acceso administrativo de tu propia cuenta.')

        rol = request.POST.get('rol', 'cliente')
        if rol not in dict(Profile.ROL_CHOICES):
            errors.append('Selecciona un rol válido.')
        elif rol in ('admin', 'operador') and not is_staff:
            errors.append('Los roles Administrador y Operador requieren acceso al panel.')
        elif is_staff and rol == 'cliente':
            errors.append('Asigna un rol administrativo o de operador para habilitar el panel.')

        if not errors:
            with transaction.atomic():
                user.username = username
                user.email = email
                user.first_name = request.POST.get('first_name', '').strip()
                user.last_name = request.POST.get('last_name', '').strip()
                user.is_staff = is_staff
                user.is_active = is_active
                if password:
                    user.set_password(password)
                user.save()
                profile, _ = Profile.objects.get_or_create(user=user)
                profile.rut = rut or None
                profile.telefono = request.POST.get('telefono', '').strip() or None
                profile.rol = rol
                profile.save()
            messages.success(request, 'Usuario guardado correctamente.')
            return redirect('backoffice:users')

    return render(request, 'backoffice/user_form.html', {
        'target_user': user if user.pk else None,
        'form_data': form_data,
        'errors': errors,
        'roles': Profile.ROL_CHOICES,
    })


@admin_required
def user_toggle_active(request, pk):
    user = get_object_or_404(User, pk=pk, is_superuser=False)
    if request.method == 'POST':
        if user.pk == request.user.pk:
            messages.error(request, 'No puedes desactivar tu propia cuenta.')
        else:
            user.is_active = not user.is_active
            user.save(update_fields=['is_active'])
            status = 'activado' if user.is_active else 'desactivado'
            messages.success(request, f'Usuario {status} correctamente.')
    return redirect('backoffice:users')


@operator_required
def order_list(request):
    orders = Order.objects.select_related('user').order_by('-creada')
    status = request.GET.get('estado', '')
    if status in dict(Order.ESTADO_CHOICES):
        orders = orders.filter(estado=status)
    return render(request, 'backoffice/orders.html', {
        'orders': orders,
        'statuses': Order.ESTADO_CHOICES,
        'selected_status': status,
    })


@operator_required
def order_form(request, pk=None):
    order = get_object_or_404(Order, pk=pk) if pk else None
    if order and (order.estado != 'pendiente' or order.transaction_id):
        messages.error(request, 'Solo se pueden editar ventas pendientes sin transacción de pago.')
        return redirect('backoffice:orders')

    customers = User.objects.filter(is_staff=False, is_superuser=False, is_active=True).order_by('username')
    products = Product.objects.filter(estado='activo').order_by('nombre')
    customer_id = str(order.user_id) if order else ''
    rows = [
        {'product_id': str(item.product_id), 'quantity': str(item.cantidad)}
        for item in order.order_items.all()
    ] if order else [{} for _ in range(5)]
    errors = []

    if request.method == 'POST':
        customer_id = request.POST.get('cliente', '')
        customer = customers.filter(pk=customer_id).first()
        if customer is None:
            errors.append('Selecciona un cliente activo.')

        product_ids = request.POST.getlist('productos')
        quantities = request.POST.getlist('cantidades')
        rows = [
            {'product_id': product_id, 'quantity': quantity}
            for product_id, quantity in zip(product_ids, quantities)
        ]
        valid_product_ids = [value for value in product_ids if value.isdigit()]
        product_map = Product.objects.filter(pk__in=valid_product_ids, estado='activo').in_bulk()
        selected_items = []
        seen_products = set()
        for product_id, quantity_text in zip(product_ids, quantities):
            if not product_id and not quantity_text:
                continue
            product = product_map.get(int(product_id)) if product_id.isdigit() else None
            if product is None:
                errors.append('Selecciona un producto válido en cada línea utilizada.')
                continue
            if product.pk in seen_products:
                errors.append('Cada producto debe aparecer una sola vez en la venta.')
                continue
            seen_products.add(product.pk)
            try:
                quantity = int(quantity_text)
                if quantity < 1:
                    raise ValueError
            except ValueError:
                errors.append(f'La cantidad de {product.nombre} debe ser mayor que cero.')
                continue
            if quantity > product.stock:
                errors.append(f'El stock disponible de {product.nombre} es {product.stock}.')
                continue
            selected_items.append((product, quantity))

        if not selected_items:
            errors.append('Agrega al menos un producto a la venta.')

        if not errors:
            with transaction.atomic():
                if order is None:
                    order = Order.objects.create(user=customer, estado='pendiente')
                else:
                    order.user = customer
                    order.order_items.all().delete()
                total = Decimal('0')
                for product, quantity in selected_items:
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        cantidad=quantity,
                        precio_unitario=product.precio,
                    )
                    total += product.precio * quantity
                order.total = total
                order.save(update_fields=['user', 'total'])
            messages.success(request, f'Venta #{order.pk} guardada como pendiente de pago.')
            return redirect('backoffice:orders')

    return render(request, 'backoffice/order_form.html', {
        'order': order,
        'customers': customers,
        'products': products,
        'customer_id': customer_id,
        'rows': rows,
        'errors': errors,
    })


@admin_required
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.estado != 'pendiente' or order.transaction_id:
        messages.error(request, 'Solo se pueden eliminar ventas pendientes sin transacción de pago.')
        return redirect('backoffice:orders')
    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Venta pendiente eliminada correctamente.')
        return redirect('backoffice:orders')
    return render(request, 'backoffice/confirm_delete.html', {
        'object': f'Venta #{order.pk} de {order.user.username}',
        'cancel_url': 'backoffice:orders',
        'heading': 'Eliminar venta pendiente',
    })


@operator_required
def order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('estado', '')
        if status not in dict(Order.ESTADO_CHOICES):
            messages.error(request, 'Selecciona un estado válido para la venta.')
        elif order.transaction_id and status not in ('pagada', 'despachada'):
            messages.error(request, 'Una venta con pago registrado no puede volver a pendiente ni cancelarse desde este panel.')
        elif not order.transaction_id and status not in ('pendiente', 'cancelada'):
            messages.error(request, 'Una venta sin transacción de pago no puede marcarse como pagada o despachada.')
        else:
            order.estado = status
            order.save(update_fields=['estado'])
            messages.success(request, f'Venta #{order.pk} actualizada correctamente.')
    return redirect('backoffice:orders')


@operator_required
def reports(request):
    errors = []
    category_id = request.GET.get('categoria', '')
    category_products = Product.objects.none()
    if category_id:
        if Category.objects.filter(pk=category_id).exists():
            category_products = Product.objects.filter(categoria_id=category_id).order_by('nombre')
        else:
            errors.append('La categoría seleccionada no existe.')

    min_price = request.GET.get('precio_min', '').strip()
    max_price = request.GET.get('precio_max', '').strip()
    price_products = Product.objects.all().order_by('precio')
    parsed_min = parsed_max = None
    for raw, label in ((min_price, 'mínimo'), (max_price, 'máximo')):
        if raw:
            try:
                parsed_value = Decimal(raw)
                if not parsed_value.is_finite() or parsed_value < 0:
                    raise InvalidOperation
                if label == 'mínimo':
                    parsed_min = parsed_value
                else:
                    parsed_max = parsed_value
            except (InvalidOperation, ValueError):
                errors.append(f'El precio {label} no es válido.')
    if parsed_min is not None and parsed_max is not None and parsed_min > parsed_max:
        errors.append('El precio mínimo no puede superar al máximo.')
    if parsed_min is not None:
        price_products = price_products.filter(precio__gte=parsed_min)
    if parsed_max is not None:
        price_products = price_products.filter(precio__lte=parsed_max)

    customers = User.objects.filter(is_staff=False, is_superuser=False).order_by('username')
    customer_id = request.GET.get('cliente', '')
    selected_customer = customers.filter(pk=customer_id).first() if customer_id else None
    if customer_id and selected_customer is None:
        errors.append('El cliente seleccionado no existe.')
    customer_orders = (
        Order.objects.filter(user=selected_customer, estado__in=('pagada', 'despachada'))
        .order_by('-creada')
        if selected_customer else Order.objects.none()
    )

    order_id = request.GET.get('orden', '')
    selected_order = Order.objects.filter(pk=order_id).first() if order_id else None
    if order_id and selected_order is None:
        errors.append('La venta seleccionada no existe.')
    selected_order_items = (
        OrderItem.objects.filter(order=selected_order).select_related('product')
        if selected_order else OrderItem.objects.none()
    )

    start_raw = request.GET.get('desde', '').strip()
    end_raw = request.GET.get('hasta', '').strip()
    start_date = parse_date(start_raw) if start_raw else None
    end_date = parse_date(end_raw) if end_raw else None
    if start_raw and start_date is None:
        errors.append('La fecha inicial no es válida.')
    if end_raw and end_date is None:
        errors.append('La fecha final no es válida.')
    if start_date and end_date and start_date > end_date:
        errors.append('La fecha inicial no puede ser posterior a la final.')
    period_orders = Order.objects.filter(estado__in=('pagada', 'despachada'))
    if start_date:
        period_orders = period_orders.filter(creada__date__gte=start_date)
    if end_date:
        period_orders = period_orders.filter(creada__date__lte=end_date)

    day_raw = request.GET.get('dia', '').strip()
    selected_day = parse_date(day_raw) if day_raw else None
    if day_raw and selected_day is None:
        errors.append('La fecha del reporte diario no es válida.')
    day_orders = Order.objects.none()
    day_total = Decimal('0')
    if selected_day:
        day_orders = Order.objects.filter(
            creada__date=selected_day,
            estado__in=('pagada', 'despachada'),
        ).select_related('user').order_by('-creada')
        day_total = day_orders.aggregate(total=Sum('total'))['total'] or Decimal('0')

    return render(request, 'backoffice/reports.html', {
        'errors': errors,
        'categories': Category.objects.order_by('name'),
        'all_products': Product.objects.select_related('categoria').order_by('nombre'),
        'category_id': category_id,
        'category_products': category_products,
        'min_price': min_price,
        'max_price': max_price,
        'price_products': price_products,
        'top_expensive': Product.objects.order_by('-precio', 'nombre')[:10],
        'customer_count': customers.count(),
        'customers': customers,
        'customer_id': customer_id,
        'selected_customer': selected_customer,
        'customer_orders': customer_orders,
        'orders_for_selection': Order.objects.select_related('user').order_by('-creada')[:200],
        'order_id': order_id,
        'selected_order': selected_order,
        'selected_order_items': selected_order_items,
        'start_raw': start_raw,
        'end_raw': end_raw,
        'period_orders': period_orders.select_related('user'),
        'period_count': period_orders.count(),
        'low_stock_products': Product.objects.filter(stock__lt=5).order_by('stock', 'nombre'),
        'day_raw': day_raw,
        'selected_day': selected_day,
        'day_orders': day_orders,
        'day_total': day_total,
    })