from django.conf import settings
from django.db import models

from apps.boards.models import Board, BoardColumn


class Ticket(models.Model):
    # Define si el caso cargado es reclamo o consulta.
    INTERACCION_CHOICES = [
        ('reclamo', 'Reclamo'),
        ('consulta', 'Consulta'),
    ]

    # Define el nivel de prioridad del ticket.
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]

    # Título visible de la tarjeta/ticket.
    titulo = models.CharField(max_length=150, blank=True)

    # Campo usado para mostrar una referencia rápida del cliente.
    cliente = models.CharField(max_length=100, blank=True)

    # Descripción general del caso.
    descripcion = models.TextField(blank=True)

    # Datos principales del cliente afectado.
    numero_contrato = models.CharField(max_length=20, default='')
    id_cliente = models.CharField(max_length=20, default='')
    correo_cliente = models.EmailField(blank=True, null=True)
    contacto_principal = models.CharField(max_length=10, default='')
    contacto_secundario = models.CharField(max_length=30, blank=True, null=True)

    # Tipo de interacción: reclamo o consulta.
    tipo_interaccion = models.CharField(
        max_length=20,
        choices=INTERACCION_CHOICES,
        default='reclamo'
    )

    # Comentario cargado por el empleado al crear el reclamo.
    detalle_reclamo = models.TextField(default='')

    # Tablero al que pertenece el ticket.
    tablero = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='tickets'
    )

    # Columna actual del ticket: pendiente, seguimiento, finalizado, etc.
    columna = models.ForeignKey(
        BoardColumn,
        on_delete=models.CASCADE,
        related_name='tickets'
    )

    # Usuario que cargó el ticket.
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tickets_creados'
    )

    # Técnico asignado para atender el caso.
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

    def save(self, *args, **kwargs):
        # Si no se carga un título manual, se genera uno automático.
        if not self.titulo:
            self.titulo = f'{self.get_tipo_interaccion_display()} - Contrato {self.numero_contrato}'

        # Si no hay nombre de cliente, se usa el ID como referencia.
        if not self.cliente:
            self.cliente = f'Cliente ID {self.id_cliente}'

        # La descripción se completa con el comentario inicial del empleado.
        if not self.descripcion:
            self.descripcion = self.detalle_reclamo

        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo


class TicketComment(models.Model):
    # Relaciona el comentario con un ticket específico.
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='comentarios'
    )

    # Usuario que escribió el comentario.
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