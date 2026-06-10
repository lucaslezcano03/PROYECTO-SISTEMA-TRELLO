from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import TicketCommentForm, TicketForm
from .models import Ticket
from apps.users.decorators import roles_permitidos
from .forms import ReclamoClienteForm
from .models import Ticket
from .services import buscar_tecnico_disponible, obtener_tablero_reclamos



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

@roles_permitidos('empleado', 'supervisor', 'admin')
def crear_reclamo_internet(request):
    # Esta vista permite que un empleado cargue un reclamo de Internet Hogar.
    if request.method == 'POST':
        form = ReclamoClienteForm(request.POST)

        if form.is_valid():
            tablero, columna_inicial = obtener_tablero_reclamos(request.user)
            tecnico_asignado = buscar_tecnico_disponible()

            # Crea el ticket usando los datos enviados desde el formulario.
            Ticket.objects.create(
                numero_contrato=form.cleaned_data['numero_contrato'],
                id_cliente=form.cleaned_data['id_cliente'],
                correo_cliente=form.cleaned_data['correo_cliente'],
                contacto_principal=form.cleaned_data['contacto_principal'],
                contacto_secundario=form.cleaned_data['contacto_secundario'],
                tipo_interaccion=form.cleaned_data['tipo_interaccion'],
                detalle_reclamo=form.cleaned_data['comentario'],
                tablero=tablero,
                columna=columna_inicial,
                creado_por=request.user,
                asignado_a=tecnico_asignado,
                prioridad='media'
            )

            messages.success(request, 'El reclamo fue cargado correctamente.')
            return redirect('tickets:reclamo_enviado')
    else:
        form = ReclamoClienteForm()

    return render(request, 'tickets/crear_reclamo.html', {
        'form': form
    })


@roles_permitidos('empleado', 'supervisor', 'admin')
def reclamo_enviado(request):
    # Pantalla simple para confirmar que el reclamo fue enviado.
    return render(request, 'tickets/reclamo_enviado.html')