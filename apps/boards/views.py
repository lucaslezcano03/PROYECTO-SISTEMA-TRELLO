from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Board


@login_required
def board_list(request):
    tableros = Board.objects.filter(
        Q(creado_por=request.user) | Q(miembros=request.user)
    ).distinct().order_by('-fecha_creacion')

    return render(request, 'boards/board_list.html', {
        'tableros': tableros
    })


@login_required
def board_detail(request, board_id):
    tablero = get_object_or_404(
        Board.objects.prefetch_related('columnas__tickets'),
        Q(id=board_id),
        Q(creado_por=request.user) | Q(miembros=request.user)
    )

    return render(request, 'boards/board_detail.html', {
        'tablero': tablero
    })