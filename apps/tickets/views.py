from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.boards.models import BoardColumn
from apps.notifications.services import crear_notificacion
from apps.users.decorators import roles_permitidos

from .forms import GestionTicketForm, ReclamoClienteForm, TicketCommentForm
from .models import Ticket
from .services import buscar_tecnico_disponible, obtener_tablero_reclamos

from django.db import transaction


@login_required
def ticket_create(request):
    # Esta vista vieja se redirige al formulario real de reclamos.
    return redirect('tickets:crear_reclamo_internet')


@roles_permitidos('tecnico', 'supervisor', 'admin')
def ticket_detail(request, ticket_id):
    # Busca el ticket y valida que el usuario tenga permiso para verlo.
    ticket = get_object_or_404(
        Ticket,
        Q(id=ticket_id),
        Q(tablero__creado_por=request.user) |
        Q(tablero__miembros=request.user) |
        Q(asignado_a=request.user)
    )

    if request.method == 'POST':
        # Este bloque se usa cuando se actualiza estado, técnico o prioridad.
        if 'guardar_cambios' in request.POST:
            tecnico_anterior = ticket.asignado_a
            columna_anterior = ticket.columna

            gestion_form = GestionTicketForm(
                request.POST,
                instance=ticket,
                tablero=ticket.tablero
            )
            comentario_form = TicketCommentForm()

            if gestion_form.is_valid():
                ticket_actualizado = gestion_form.save()

                # Si cambió el técnico, se crea notificación al nuevo asignado.
                if ticket_actualizado.asignado_a != tecnico_anterior:
                    crear_notificacion(
                        ticket_actualizado.asignado_a,
                        f'Se te asignó el ticket: {ticket_actualizado.titulo}'
                    )

                # Si cambió el estado, se registra como comentario automático.
                if ticket_actualizado.columna != columna_anterior:
                    ticket_actualizado.comentarios.create(
                        usuario=request.user,
                        mensaje=f'Estado cambiado de {columna_anterior.nombre} a {ticket_actualizado.columna.nombre}.'
                    )

                messages.success(request, 'El ticket fue actualizado correctamente.')
                return redirect('tickets:ticket_detail', ticket_id=ticket.id)

        # Este bloque se usa cuando se agrega un comentario de seguimiento.
        elif 'agregar_comentario' in request.POST:
            comentario_form = TicketCommentForm(request.POST)
            gestion_form = GestionTicketForm(instance=ticket, tablero=ticket.tablero)

            if comentario_form.is_valid():
                comentario = comentario_form.save(commit=False)
                comentario.ticket = ticket
                comentario.usuario = request.user
                comentario.save()

                messages.success(request, 'Comentario agregado correctamente.')
                return redirect('tickets:ticket_detail', ticket_id=ticket.id)

    else:
        gestion_form = GestionTicketForm(instance=ticket, tablero=ticket.tablero)
        comentario_form = TicketCommentForm()

    return render(request, 'tickets/ticket_detail.html', {
        'ticket': ticket,
        'gestion_form': gestion_form,
        'comentario_form': comentario_form,
    })

@roles_permitidos('empleado', 'tecnico', 'supervisor', 'admin')
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

@roles_permitidos('tecnico', 'supervisor', 'admin')
def gestion_reclamos(request):
    # Obtiene o crea el tablero oficial de reclamos de Internet Hogar.
    tablero, columna_inicial = obtener_tablero_reclamos(request.user)

    # Obtiene solamente las columnas de ese tablero.
    columnas = tablero.columnas.prefetch_related('tickets').order_by('posicion')

    return render(request, 'tickets/gestion_reclamos.html', {
        'tablero': tablero,
        'columnas': columnas,
    })

@require_POST
@roles_permitidos('tecnico', 'supervisor', 'admin')
def mover_ticket(request, ticket_id):
    # Esta vista funciona como una API interna para mover tickets por drag & drop.
    ticket = get_object_or_404(Ticket, id=ticket_id)

    columna_id = request.POST.get('columna_id')

    # Valida que el frontend haya enviado la columna destino.
    if not columna_id:
        return JsonResponse({
            'ok': False,
            'error': 'No se recibió la columna destino.'
        }, status=400)

    nueva_columna = get_object_or_404(BoardColumn, id=columna_id)

    # Evita mover tickets a columnas de otro tablero.
    if nueva_columna.tablero_id != ticket.tablero_id:
        return JsonResponse({
            'ok': False,
            'error': 'La columna no pertenece al tablero del ticket.'
        }, status=400)

    columna_anterior = ticket.columna

    # Si el ticket se suelta en la misma columna, no se modifica nada.
    if columna_anterior.id == nueva_columna.id:
        return JsonResponse({
            'ok': True,
            'mensaje': 'El ticket ya estaba en esa columna.',
            'nuevo_estado': nueva_columna.nombre
        })

    with transaction.atomic():
        # Actualiza el estado del ticket.
        ticket.columna = nueva_columna
        ticket.save()

        # Guarda un seguimiento automático dentro del ticket.
        ticket.comentarios.create(
            usuario=request.user,
            mensaje=f'Ticket movido de {columna_anterior.nombre} a {nueva_columna.nombre}.'
        )

        # Notifica al técnico asignado, si existe.
        if ticket.asignado_a:
            crear_notificacion(
                ticket.asignado_a,
                f'El ticket "{ticket.titulo}" fue movido a {nueva_columna.nombre}.'
            )

    return JsonResponse({
        'ok': True,
        'ticket_id': ticket.id,
        'nuevo_estado': nueva_columna.nombre
    })