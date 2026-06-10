from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    # Muestra datos importantes del perfil en el admin.
    list_display = ('usuario', 'rol', 'disponible')

    # Permite filtrar usuarios por rol o disponibilidad.
    list_filter = ('rol', 'disponible')

    # Permite buscar por nombre de usuario.
    search_fields = ('usuario__username',)