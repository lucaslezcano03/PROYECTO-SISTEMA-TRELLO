# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F, Prefetch, Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

# Django Channels y WebSockets
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# Django REST Framework
from rest_framework import status
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
)
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Aplicaciones del proyecto
from apps.boards.models import BoardColumn
from apps.notifications.services import crear_notificacion
from apps.users.decorators import roles_permitidos
from apps.users.permissions import (
    puede_cargar_reclamos,
    puede_mover_ticket,
    puede_ver_ticket,
)

# Archivos de la app tickets
from .forms import (
    GestionTicketForm,
    ReclamoClienteForm,
    TicketCommentForm,
)
from .models import Ticket
from .services import (
    buscar_tecnico_disponible,
    obtener_tablero_reclamos,
)


@login_required
def ticket_create(request):
    # Esta vista vieja se redirige al formulario real de reclamos.
    return redirect('tickets:crear_reclamo_internet')


@roles_permitidos('tecnico', 'supervisor', 'admin')
def ticket_detail(request, ticket_id):
    # Busca el ticket solicitado.
    ticket = get_object_or_404(
        Ticket.objects.select_related('tablero', 'columna', 'asignado_a'),
        id=ticket_id
    )

    # Evita que un técnico entre por URL a tickets que no son suyos.
    if not puede_ver_ticket(request.user, ticket):
        return HttpResponseForbidden('No tenés permiso para ver este ticket.')

    if request.method == 'POST':
        if 'guardar_cambios' in request.POST:
            tecnico_anterior = ticket.asignado_a
            columna_anterior = ticket.columna

            gestion_form = GestionTicketForm(
                request.POST,
                instance=ticket,
                tablero=ticket.tablero,
                usuario=request.user
            )

            comentario_form = TicketCommentForm()

            if gestion_form.is_valid():
                ticket_actualizado = gestion_form.save()

                if ticket_actualizado.asignado_a != tecnico_anterior:
                    crear_notificacion(
                        ticket_actualizado.asignado_a,
                        f'Se te asignó el ticket: {ticket_actualizado.titulo}'
                    )

                if ticket_actualizado.columna != columna_anterior:
                    ticket_actualizado.comentarios.create(
                        usuario=request.user,
                        mensaje=f'Estado cambiado de {columna_anterior.nombre} a {ticket_actualizado.columna.nombre}.'
                    )

                messages.success(request, 'El ticket fue actualizado correctamente.')
                return redirect('tickets:ticket_detail', ticket_id=ticket.id)

        elif 'agregar_comentario' in request.POST:
            comentario_form = TicketCommentForm(request.POST)

            gestion_form = GestionTicketForm(
                instance=ticket,
                tablero=ticket.tablero,
                usuario=request.user
            )

            if comentario_form.is_valid():
                comentario = comentario_form.save(commit=False)
                comentario.ticket = ticket
                comentario.usuario = request.user
                comentario.save()

                messages.success(request, 'Comentario agregado correctamente.')
                return redirect('tickets:ticket_detail', ticket_id=ticket.id)

    else:
        gestion_form = GestionTicketForm(
            instance=ticket,
            tablero=ticket.tablero,
            usuario=request.user
        )

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


@roles_permitidos('empleado', 'tecnico', 'supervisor', 'admin')
def reclamo_enviado(request):
    # Pantalla simple para confirmar que el reclamo fue enviado.
    return render(request, 'tickets/reclamo_enviado.html')

@roles_permitidos('tecnico', 'supervisor', 'admin')
def gestion_reclamos(request):
    # Obtiene o crea el tablero oficial de reclamos.
    tablero, columna_inicial = obtener_tablero_reclamos(request.user)

    # Base de tickets visibles dentro del tablero.
    tickets_visibles = Ticket.objects.filter(
        tablero=tablero
    ).select_related(
        'asignado_a',
        'columna'
    ).order_by(
    'posicion',
    'fecha_creacion',
    'id'
    )

    # Si el usuario es técnico, solo ve tickets asignados a él.
    if not request.user.is_superuser:
        perfil = getattr(request.user, 'perfil', None)

        if perfil and perfil.rol == 'tecnico':
            tickets_visibles = tickets_visibles.filter(asignado_a=request.user)

    # Precarga los tickets filtrados dentro de cada columna.
    columnas = tablero.columnas.prefetch_related(
        Prefetch('tickets', queryset=tickets_visibles)
    ).order_by('posicion')

    return render(request, 'tickets/gestion_reclamos.html', {
        'tablero': tablero,
        'columnas': columnas,
    })

def normalizar_posiciones(columna):
    """
    Ordena los tickets de una columna y les asigna
    posiciones consecutivas: 0, 1, 2, 3...
    """
    tickets = Ticket.objects.filter(
        columna=columna
    ).order_by(
        'posicion',
        'fecha_creacion',
        'id'
    )

    for nueva_posicion, ticket in enumerate(tickets):
        if ticket.posicion != nueva_posicion:
            Ticket.objects.filter(
                id=ticket.id
            ).update(
                posicion=nueva_posicion
            )

@require_POST
@roles_permitidos('tecnico', 'supervisor', 'admin')
def mover_ticket(request, ticket_id):
    """
    Mueve un ticket a otra columna y guarda
    su posición exacta dentro de esa columna.
    """
    ticket = get_object_or_404(
        Ticket.objects.select_related(
            'columna',
            'tablero',
            'asignado_a'
        ),
        id=ticket_id
    )

    # El técnico solo puede mover tickets asignados a él.
    if not puede_mover_ticket(request.user, ticket):
        return JsonResponse({
            'ok': False,
            'error': 'No tenés permiso para mover este ticket.'
        }, status=403)

    columna_id = request.POST.get('columna_id')
    posicion_recibida = request.POST.get('posicion', 0)

    if not columna_id:
        return JsonResponse({
            'ok': False,
            'error': 'No se recibió la columna destino.'
        }, status=400)

    try:
        nueva_posicion = max(0, int(posicion_recibida))
    except (TypeError, ValueError):
        return JsonResponse({
            'ok': False,
            'error': 'La posición recibida no es válida.'
        }, status=400)

    nueva_columna = get_object_or_404(
        BoardColumn,
        id=columna_id
    )

    # Impide mover una tarjeta a una columna de otro tablero.
    if nueva_columna.tablero_id != ticket.tablero_id:
        return JsonResponse({
            'ok': False,
            'error': 'La columna no pertenece al tablero del ticket.'
        }, status=400)

    columna_anterior = ticket.columna

    with transaction.atomic():
        # Corrige las posiciones existentes antes del movimiento.
        normalizar_posiciones(columna_anterior)

        if nueva_columna.id != columna_anterior.id:
            normalizar_posiciones(nueva_columna)

        # Vuelve a consultar el ticket después de normalizar.
        ticket = Ticket.objects.select_for_update().get(
            id=ticket.id
        )

        posicion_anterior = ticket.posicion

        cantidad_destino = Ticket.objects.filter(
            columna=nueva_columna
        ).exclude(
            id=ticket.id
        ).count()

        # Evita guardar una posición mayor a la cantidad de tarjetas.
        nueva_posicion = min(
            nueva_posicion,
            cantidad_destino
        )

        if columna_anterior.id == nueva_columna.id:
            # Reordenamiento dentro de la misma columna.
            if nueva_posicion < posicion_anterior:
                Ticket.objects.filter(
                    columna=nueva_columna,
                    posicion__gte=nueva_posicion,
                    posicion__lt=posicion_anterior
                ).exclude(
                    id=ticket.id
                ).update(
                    posicion=F('posicion') + 1
                )

            elif nueva_posicion > posicion_anterior:
                Ticket.objects.filter(
                    columna=nueva_columna,
                    posicion__gt=posicion_anterior,
                    posicion__lte=nueva_posicion
                ).exclude(
                    id=ticket.id
                ).update(
                    posicion=F('posicion') - 1
                )

        else:
            # Cierra el espacio que deja en la columna anterior.
            Ticket.objects.filter(
                columna=columna_anterior,
                posicion__gt=posicion_anterior
            ).update(
                posicion=F('posicion') - 1
            )

            # Abre espacio en la columna destino.
            Ticket.objects.filter(
                columna=nueva_columna,
                posicion__gte=nueva_posicion
            ).update(
                posicion=F('posicion') + 1
            )

        ticket.columna = nueva_columna
        ticket.posicion = nueva_posicion
        ticket.save(
            update_fields=[
                'columna',
                'posicion',
                'fecha_actualizacion'
            ]
        )

        # Solo registra seguimiento si realmente cambió de estado.
        if columna_anterior.id != nueva_columna.id:
            ticket.comentarios.create(
                usuario=request.user,
                mensaje=(
                    f'Ticket movido de {columna_anterior.nombre} '
                    f'a {nueva_columna.nombre}.'
                )
            )

            if ticket.asignado_a:
                crear_notificacion(
                    ticket.asignado_a,
                    f'El ticket "{ticket.titulo}" fue movido '
                    f'a {nueva_columna.nombre}.'
                )

    # Envía el nuevo estado y posición mediante WebSocket.
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        'tablero_reclamos',
        {
            'type': 'ticket.movido',
            'ticket_id': ticket.id,
            'columna_id': nueva_columna.id,
            'posicion': nueva_posicion,
            'nuevo_estado': nueva_columna.nombre,
            'movido_por': request.user.username,
        }
    )

    return JsonResponse({
        'ok': True,
        'ticket_id': ticket.id,
        'columna_id': nueva_columna.id,
        'posicion': nueva_posicion,
        'nuevo_estado': nueva_columna.nombre
    })

def ticket_a_json(ticket):
    # Convierte un ticket del modelo Django a un diccionario JSON.
    return {
        'id': ticket.id,
        'titulo': ticket.titulo,
        'numero_contrato': ticket.numero_contrato,
        'id_cliente': ticket.id_cliente,
        'correo_cliente': ticket.correo_cliente,
        'contacto_principal': ticket.contacto_principal,
        'contacto_secundario': ticket.contacto_secundario,
        'tipo_interaccion': ticket.tipo_interaccion,
        'detalle_reclamo': ticket.detalle_reclamo,
        'prioridad': ticket.prioridad,
        'estado': ticket.columna.nombre if ticket.columna else None,
        'tablero': ticket.tablero.nombre if ticket.tablero else None,
        'creado_por': ticket.creado_por.username if ticket.creado_por else None,
        'asignado_a': ticket.asignado_a.username if ticket.asignado_a else None,
        'fecha_creacion': ticket.fecha_creacion,
    }


@api_view(['GET', 'POST'])
@authentication_classes([BasicAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def api_tickets(request):
    # API para listar tickets y crear nuevos reclamos desde Postman o terminal.

    if request.method == 'GET':
        tablero, columna_inicial = obtener_tablero_reclamos(request.user)

        tickets = Ticket.objects.filter(
            tablero=tablero
        ).select_related(
            'tablero',
            'columna',
            'creado_por',
            'asignado_a'
        ).order_by(
            '-fecha_creacion'
        )

        # El técnico solo ve tickets asignados a él.
        if not request.user.is_superuser:
            perfil = getattr(request.user, 'perfil', None)

            if perfil and perfil.rol == 'tecnico':
                tickets = tickets.filter(asignado_a=request.user)

            elif perfil and perfil.rol == 'empleado':
                tickets = tickets.filter(creado_por=request.user)

        datos = [ticket_a_json(ticket) for ticket in tickets]

        return Response({
            'ok': True,
            'cantidad': len(datos),
            'tickets': datos
        })

    if request.method == 'POST':
        # Valida si el usuario tiene permiso para cargar reclamos.
        if not puede_cargar_reclamos(request.user):
            return Response({
                'ok': False,
                'error': 'No tenés permiso para crear tickets.'
            }, status=status.HTTP_403_FORBIDDEN)

        form = ReclamoClienteForm(request.data)

        if not form.is_valid():
            return Response({
                'ok': False,
                'errores': form.errors.get_json_data()
            }, status=status.HTTP_400_BAD_REQUEST)

        tablero, columna_inicial = obtener_tablero_reclamos(request.user)
        tecnico_asignado = buscar_tecnico_disponible()

        ticket = Ticket.objects.create(
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

        if tecnico_asignado:
            crear_notificacion(
                tecnico_asignado,
                f'Se te asignó el ticket: {ticket.titulo}'
            )

        return Response({
            'ok': True,
            'mensaje': 'Ticket creado correctamente desde la API.',
            'ticket': ticket_a_json(ticket)
        }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@authentication_classes([BasicAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def api_ticket_detail(request, ticket_id):
    # API para consultar el detalle de un ticket específico.
    ticket = get_object_or_404(
        Ticket.objects.select_related(
            'tablero',
            'columna',
            'creado_por',
            'asignado_a'
        ),
        id=ticket_id
    )

    if not puede_ver_ticket(request.user, ticket):
        return Response({
            'ok': False,
            'error': 'No tenés permiso para ver este ticket.'
        }, status=status.HTTP_403_FORBIDDEN)

    return Response({
        'ok': True,
        'ticket': ticket_a_json(ticket)
    })

@api_view(['GET'])
@authentication_classes([BasicAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def api_estado_sistema(request):
    # API simple para comprobar que el backend está funcionando.
    perfil = getattr(request.user, 'perfil', None)

    if request.user.is_superuser:
        rol = 'admin'
    elif perfil:
        rol = perfil.rol
    else:
        rol = 'sin perfil'

    return Response({
        'ok': True,
        'sistema': 'Sistema de Tickets Técnicos',
        'api': 'activa',
        'usuario': request.user.username,
        'rol': rol,
        'mensaje': 'Backend funcionando correctamente.'
    })