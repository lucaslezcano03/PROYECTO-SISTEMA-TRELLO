def datos_usuario(request):
    # Envía datos del rol del usuario a todos los templates.
    if not request.user.is_authenticated:
        return {
            'rol_usuario': None,
            'es_empleado': False,
            'es_tecnico': False,
            'es_supervisor': False,
            'es_admin_sistema': False,
        }

    if request.user.is_superuser:
        rol = 'admin'
    else:
        perfil = getattr(request.user, 'perfil', None)
        rol = perfil.rol if perfil else None

    return {
        'rol_usuario': rol,
        'es_empleado': rol == 'empleado',
        'es_tecnico': rol == 'tecnico',
        'es_supervisor': rol == 'supervisor',
        'es_admin_sistema': rol == 'admin' or request.user.is_superuser,
    }