from django.contrib import admin
from .models import Ticket, TicketComment


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        'titulo',
        'cliente',
        'tablero',
        'columna',
        'asignado_a',
        'prioridad',
        'fecha_creacion',
    )
    list_filter = ('prioridad', 'columna', 'tablero')
    search_fields = ('titulo', 'cliente', 'descripcion')


@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'usuario', 'fecha_creacion')
    search_fields = ('mensaje',)