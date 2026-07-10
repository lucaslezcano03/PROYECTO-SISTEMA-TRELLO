from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    # Permite editar el perfil del usuario dentro del mismo formulario de User.
    model = UserProfile
    can_delete = False
    extra = 0
    fields = ('rol', 'disponible')


try:
    # Se elimina el registro original de User para poder personalizarlo.
    admin.site.unregister(User)
except NotRegistered:
    pass


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Agrega el perfil dentro de la pantalla de usuarios.
    inlines = (UserProfileInline,)

    # Muestra datos útiles en el listado de usuarios.
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'obtener_rol',
        'esta_disponible',
    )

    def obtener_rol(self, obj):
        # Devuelve el rol del usuario si tiene perfil.
        if hasattr(obj, 'perfil'):
            return obj.perfil.get_rol_display()
        return 'Sin perfil'

    obtener_rol.short_description = 'Rol'

    def esta_disponible(self, obj):
        # Indica si el técnico está disponible para recibir tickets.
        if hasattr(obj, 'perfil'):
            return obj.perfil.disponible
        return False

    esta_disponible.boolean = True
    esta_disponible.short_description = 'Disponible'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    # Administración directa de perfiles.
    list_display = ('usuario', 'rol', 'disponible')
    list_filter = ('rol', 'disponible')
    search_fields = ('usuario__username', 'usuario__email')