def obtener_rol_usuario(usuario):
    # Devuelve el rol real del usuario dentro del sistema.
    if not usuario.is_authenticated:
        return None

    if usuario.is_superuser:
        return 'admin'

    perfil = getattr(usuario, 'perfil', None)

    if not perfil:
        return None

    return perfil.rol


def puede_cargar_reclamos(usuario):
    # Define quién puede cargar reclamos.
    rol = obtener_rol_usuario(usuario)

    return rol in ['empleado', 'tecnico', 'supervisor', 'admin']


def puede_ver_gestion(usuario):
    # Define quién puede entrar al tablero de gestión.
    rol = obtener_rol_usuario(usuario)

    return rol in ['tecnico', 'supervisor', 'admin']


def puede_reasignar_tickets(usuario):
    # Solo supervisor y admin pueden reasignar técnicos.
    rol = obtener_rol_usuario(usuario)

    return rol in ['supervisor', 'admin']


def puede_mover_ticket(usuario, ticket):
    # Supervisor y admin pueden mover cualquier ticket.
    rol = obtener_rol_usuario(usuario)

    if rol in ['supervisor', 'admin']:
        return True

    # El técnico solo puede mover tickets asignados a él.
    if rol == 'tecnico' and ticket.asignado_a_id == usuario.id:
        return True

    return False


def puede_ver_ticket(usuario, ticket):
    # Supervisor y admin pueden ver cualquier ticket.
    rol = obtener_rol_usuario(usuario)

    if rol in ['supervisor', 'admin']:
        return True

    # El técnico solo puede ver tickets asignados a él.
    if rol == 'tecnico' and ticket.asignado_a_id == usuario.id:
        return True

    return False