def notificaciones_usuario(request):
    # Envía al template la cantidad de notificaciones no leídas del usuario.
    if request.user.is_authenticated:
        cantidad = request.user.notificaciones.filter(leida=False).count()

        return {
            'notificaciones_no_leidas': cantidad
        }

    return {
        'notificaciones_no_leidas': 0
    }