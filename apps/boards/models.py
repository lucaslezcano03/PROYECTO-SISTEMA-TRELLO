from django.conf import settings
from django.db import models


class Board(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tableros_creados'
    )
    miembros = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='tableros_asignados',
        blank=True
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class BoardColumn(models.Model):
    tablero = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='columnas'
    )
    nombre = models.CharField(max_length=80)
    posicion = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['posicion']

    def __str__(self):
        return f'{self.nombre} - {self.tablero.nombre}'