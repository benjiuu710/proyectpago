from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False


class UserAdminConPerfil(UserAdmin):
    inlines = (ProfileInline,)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'rut', 'telefono', 'pais', 'moneda', 'rol', 'estado')
    list_filter = ('pais', 'rol', 'estado')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'rut', 'telefono')


admin.site.unregister(User)
admin.site.register(User, UserAdminConPerfil)
