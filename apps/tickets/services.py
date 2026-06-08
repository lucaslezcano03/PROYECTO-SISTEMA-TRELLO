from django.contrib.auth import get_user_model
from django.db.models import Count

from apps.boards.models import Board, BoardColumn


def obtener_tablero_reclamos(usuario_creador):
    # Crea o recupera el tablero principal de reclamos.
    tablero, _ = Board.objects.get_or_create(
        nombre='Campaña Reclamos Internet Hogar',
        defaults={
            'descripcion': 'Tablero para gestionar reclamos y consultas de clientes de Internet Hogar.',
            'creado_por': usuario_creador,
        }
    )

    columnas_base = [
        ('Pendiente', 1),
        ('En seguimiento', 2),
        ('Finalizado', 3),
    ]

    # Crea las columnas base si todavía no existen.
    for nombre_columna, posicion in columnas_base:
        BoardColumn.objects.get_or_create(
            tablero=tablero,
            nombre=nombre_columna,
            defaults={'posicion': posicion}
        )

    columna_inicial = BoardColumn.objects.get(
        tablero=tablero,
        nombre='Pendiente'
    )

    return tablero, columna_inicial


def buscar_tecnico_disponible():
    # Busca técnicos disponibles y elige al que tenga menos tickets asignados.
    Usuario = get_user_model()

    return Usuario.objects.filter(
        perfil__rol='tecnico',
        perfil__disponible=True
    ).annotate(
        cantidad_tickets=Count('tickets_asignados')
    ).order_by(
        'cantidad_tickets',
        'id'
    ).first()