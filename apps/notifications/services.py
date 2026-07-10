from .models import Notification

def crear_notificacion(usuario, mensaje):
    # Crea una notificación para un usuario específico.
    if not usuario:
        return None

    return Notification.objects.create(
        usuario=usuario,
        mensaje=mensaje
    )