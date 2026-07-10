from django.contrib import admin
from .models import Ticket, TicketComment


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    # Columnas visibles en el listado de tickets.
    list_display = (
        'titulo',
        'numero_contrato',
        'id_cliente',
        'contacto_principal',
        'tipo_interaccion',
        'columna',
        'asignado_a',
        'prioridad',
        'fecha_creacion',
    )

    # Filtros rápidos para buscar tickets según estado, prioridad o técnico.
    list_filter = (
        'tipo_interaccion',
        'prioridad',
        'columna',
        'asignado_a',
    )

    # Campos que se pueden buscar desde el admin.
    search_fields = (
        'titulo',
        'numero_contrato',
        'id_cliente',
        'contacto_principal',
        'detalle_reclamo',
    )


@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'usuario', 'fecha_creacion')
    search_fields = ('mensaje',)