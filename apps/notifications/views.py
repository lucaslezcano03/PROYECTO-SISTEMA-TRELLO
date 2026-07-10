from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Notification


@login_required
def notification_list(request):
    # Muestra las últimas notificaciones del usuario logueado.
    notificaciones = request.user.notificaciones.all()[:50]

    return render(request, 'notifications/notification_list.html', {
        'notificaciones': notificaciones
    })


@login_required
@require_POST
def notification_mark_read(request, notification_id):
    # Marca una notificación como leída.
    notificacion = get_object_or_404(
        Notification,
        id=notification_id,
        usuario=request.user
    )

    notificacion.leida = True
    notificacion.save()

    messages.success(request, 'Notificación marcada como leída.')
    return redirect('notifications:notification_list')


@login_required
@require_POST
def notification_mark_all_read(request):
    # Marca todas las notificaciones del usuario como leídas.
    request.user.notificaciones.filter(leida=False).update(leida=True)

    messages.success(request, 'Todas las notificaciones fueron marcadas como leídas.')
    return redirect('notifications:notification_list')