from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q

from apps.boards.models import Board, BoardColumn
from .models import Ticket, TicketComment


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = [
            'titulo',
            'cliente',
            'descripcion',
            'tablero',
            'columna',
            'asignado_a',
            'prioridad',
        ]

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)

        if usuario:
            tableros_usuario = Board.objects.filter(
                Q(creado_por=usuario) | Q(miembros=usuario)
            ).distinct()

            self.fields['tablero'].queryset = tableros_usuario
            self.fields['columna'].queryset = BoardColumn.objects.filter(
                tablero__in=tableros_usuario
            )

            Usuario = get_user_model()
            self.fields['asignado_a'].queryset = Usuario.objects.filter(
                Q(tableros_creados__in=tableros_usuario) |
                Q(tableros_asignados__in=tableros_usuario)
            ).distinct()

    def clean(self):
        datos = super().clean()
        tablero = datos.get('tablero')
        columna = datos.get('columna')

        if tablero and columna and columna.tablero != tablero:
            raise forms.ValidationError(
                'La columna seleccionada no pertenece al tablero indicado.'
            )

        return datos


class TicketCommentForm(forms.ModelForm):
    class Meta:
        model = TicketComment
        fields = ['mensaje']