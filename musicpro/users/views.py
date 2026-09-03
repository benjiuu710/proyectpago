from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from payments.models import BeatPayWallet
from loyalty.models import PointsWallet
from .models import Profile


def registro(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        rut = request.POST.get('rut')
        telefono = request.POST.get('telefono')
        pais = request.POST.get('pais', 'CL')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        bpass = request.POST.get('bpass', '')
        bpass2 = request.POST.get('bpass2', '')

        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'users/registro.html')

        if not (bpass.isdigit() and len(bpass) == 6) or bpass != bpass2:
            messages.error(request, 'El BPass debe tener 6 dígitos iguales en ambos campos.')
            return render(request, 'users/registro.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe.')
            return render(request, 'users/registro.html')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.profile.rut = rut
        user.profile.telefono = telefono
        user.profile.pais = pais if pais in Profile.COUNTRY_CURRENCY else 'CL'
        user.profile.moneda = Profile.COUNTRY_CURRENCY[user.profile.pais][0]
        user.profile.bpass_hash = make_password(bpass)
        user.profile.save()
        login(request, user)
        messages.success(request, f'¡Bienvenido, {username}!')
        return redirect('store:inicio')

    return render(request, 'users/registro.html')


def iniciar_sesion(request):
    if request.method == 'POST':
        identificador = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        usuario = User.objects.filter(profile__rut__iexact=identificador).first()
        username = usuario.username if usuario else identificador
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            destino = request.GET.get('next') or request.POST.get('next')
            if not destino:
                destino = 'admin:index' if user.is_staff else 'store:inicio'
            return redirect(destino)
        messages.error(request, 'RUT, usuario o contraseña incorrectos.')
    return render(request, 'users/login.html')


def cerrar_sesion(request):
    logout(request)
    return redirect('users:login')


def validar_bpass(user, bpass):
    return bool(bpass and user.profile.bpass_hash and check_password(bpass, user.profile.bpass_hash))


@login_required
def perfil(request):
    return render(request, 'users/perfil.html', {
        'perfil': request.user.profile,
        'wallet': BeatPayWallet.objects.filter(user=request.user).first(),
        'points_wallet': PointsWallet.objects.filter(user=request.user).first(),
    })
