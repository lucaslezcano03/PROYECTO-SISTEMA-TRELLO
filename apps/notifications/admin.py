from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    # Muestra datos principales de la notificación en el admin.
    list_display = ('usuario', 'mensaje', 'leida', 'fecha_creacion')

    # Permite filtrar notificaciones leídas y no leídas.
    list_filter = ('leida',)

    # Permite buscar por mensaje o usuario.
    search_fields = ('mensaje', 'usuario__username')