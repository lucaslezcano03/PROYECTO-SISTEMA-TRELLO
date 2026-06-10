from .models import Notification


def crear_notificacion(usuario, mensaje):
    # Crea una notificación solo si existe un usuario destinatario.
    if usuario:
        Notification.objects.create(
            usuario=usuario,
            mensaje=mensaje
        )