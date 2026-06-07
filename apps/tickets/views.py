from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import TicketCommentForm, TicketForm
from .models import Ticket


@login_required
def ticket_create(request):
    if request.method == 'POST':
        form = TicketForm(request.POST, usuario=request.user)

        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.creado_por = request.user
            ticket.save()

            return redirect('boards:board_detail', board_id=ticket.tablero.id)
    else:
        form = TicketForm(usuario=request.user)

    return render(request, 'tickets/ticket_form.html', {
        'form': form
    })


@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(
        Ticket,
        Q(id=ticket_id),
        Q(tablero__creado_por=request.user) | Q(tablero__miembros=request.user)
    )

    if request.method == 'POST':
        form = TicketCommentForm(request.POST)

        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.ticket = ticket
            comentario.usuario = request.user
            comentario.save()

            return redirect('tickets:ticket_detail', ticket_id=ticket.id)
    else:
        form = TicketCommentForm()

    return render(request, 'tickets/ticket_detail.html', {
        'ticket': ticket,
        'form': form
    })