from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


def roles_permitidos(*roles):
    # Este decorador permite limitar una vista según el rol del usuario.
    def decorador(vista):
        @login_required
        def wrapper(request, *args, **kwargs):
            # El superusuario siempre puede entrar.
            if request.user.is_superuser:
                return vista(request, *args, **kwargs)

            perfil = getattr(request.user, 'perfil', None)

            # Si no tiene perfil, no se le permite acceder.
            if not perfil:
                return HttpResponseForbidden('No tenés un perfil asignado.')

            # Si el rol está permitido, puede entrar a la vista.
            if perfil.rol in roles:
                return vista(request, *args, **kwargs)

            return HttpResponseForbidden('No tenés permiso para acceder a esta vista.')

        return wrapper

    return decorador