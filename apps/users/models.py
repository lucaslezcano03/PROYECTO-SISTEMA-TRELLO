from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    # Define el rol que tendrá cada usuario dentro del sistema.
    ROL_CHOICES = [
        ('empleado', 'Empleado'),
        ('tecnico', 'Técnico'),
        ('supervisor', 'Supervisor'),
        ('admin', 'Administrador'),
    ]

    # Relaciona este perfil con un usuario real de Django.
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil'
    )

    # Guarda si el usuario es empleado, técnico, supervisor o admin.
    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default='empleado'
    )

    # Sirve para saber si un técnico puede recibir tickets automáticamente.
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.usuario.username} - {self.get_rol_display()}'
