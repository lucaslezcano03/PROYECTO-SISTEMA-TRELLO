from django.conf import settings
from django.db import models
from apps.boards.models import Board, BoardColumn


class Ticket(models.Model):
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]

    titulo = models.CharField(max_length=150)
    cliente = models.CharField(max_length=100)
    descripcion = models.TextField()

    tablero = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='tickets'
    )

    columna = models.ForeignKey(
        BoardColumn,
        on_delete=models.CASCADE,
        related_name='tickets'
    )

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tickets_creados'
    )

    asignado_a = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='tickets_asignados',
        blank=True,
        null=True
    )

    prioridad = models.CharField(
        max_length=20,
        choices=PRIORIDAD_CHOICES,
        default='media'
    )

    posicion = models.PositiveIntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['posicion', '-fecha_creacion']

    def __str__(self):
        return self.titulo


class TicketComment(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='comentarios'
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    mensaje = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha_creacion']

    def __str__(self):
        return f'Comentario de {self.usuario.username}'