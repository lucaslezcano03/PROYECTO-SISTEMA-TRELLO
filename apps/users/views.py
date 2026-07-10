from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import RegistroEmpleadoForm
from .models import UserProfile


@login_required
def inicio_por_rol(request):
    # Redirige al usuario según su rol dentro del sistema.
    if request.user.is_superuser:
        return redirect('tickets:gestion_reclamos')

    perfil = getattr(request.user, 'perfil', None)

    if not perfil:
        return redirect('tickets:crear_reclamo_internet')

    if perfil.rol == 'empleado':
        return redirect('tickets:crear_reclamo_internet')

    if perfil.rol in ['tecnico', 'supervisor', 'admin']:
        return redirect('tickets:gestion_reclamos')

    return redirect('tickets:crear_reclamo_internet')


def registro_empleado(request):
    # Permite registrar empleados nuevos.
    # Por seguridad, el registro público crea solo usuarios con rol empleado.
    if request.method == 'POST':
        form = RegistroEmpleadoForm(request.POST)

        if form.is_valid():
            usuario = form.save()

            # Asegura que el usuario registrado tenga perfil de empleado.
            UserProfile.objects.update_or_create(
                usuario=usuario,
                defaults={
                    'rol': 'empleado',
                    'disponible': False,
                }
            )

            login(request, usuario)
            messages.success(request, 'Usuario registrado correctamente.')
            return redirect('users:inicio_por_rol')
    else:
        form = RegistroEmpleadoForm()

    return render(request, 'registration/register.html', {
        'form': form
    })
