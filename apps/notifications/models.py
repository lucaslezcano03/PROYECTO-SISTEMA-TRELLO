from django.conf import settings
from django.db import models


class Notification(models.Model):
    # Usuario que recibe la notificación.
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificaciones'
    )

    # Texto corto que explica qué ocurrió.
    mensaje = models.CharField(max_length=200)

    # Indica si la notificación ya fue vista.
    leida = models.BooleanField(default=False)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.mensaje