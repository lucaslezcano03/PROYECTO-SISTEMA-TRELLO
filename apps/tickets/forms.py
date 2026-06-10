from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q

from apps.boards.models import Board, BoardColumn
from .models import Ticket, TicketComment
from django.core.validators import RegexValidator


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

solo_numeros = RegexValidator(
    regex=r'^\d+$',
    message='Este campo solo permite números.'
)


telefono_paraguay = RegexValidator(
    regex=r'^09\d{8}$',
    message='Ingrese un número paraguayo válido. Ejemplo: 0983325952.'
)


class ReclamoClienteForm(forms.Form):
    # Número de contrato del cliente afectado.
    numero_contrato = forms.CharField(
        label='N° de Contrato',
        max_length=20,
        validators=[solo_numeros]
    )

    # ID del cliente afectado.
    id_cliente = forms.CharField(
        label='ID Cliente',
        max_length=20,
        validators=[solo_numeros]
    )

    # Correo opcional del cliente.
    correo_cliente = forms.EmailField(
        label='Correo del cliente',
        required=False
    )

    # Teléfono principal paraguayo obligatorio.
    contacto_principal = forms.CharField(
        label='N° de contacto principal',
        max_length=10,
        validators=[telefono_paraguay]
    )

    # Teléfono secundario opcional.
    contacto_secundario = forms.CharField(
        label='N° de contacto secundario',
        max_length=30,
        required=False,
        validators=[solo_numeros]
    )

    # Tipo de interacción del caso.
    tipo_interaccion = forms.ChoiceField(
        label='Interacción',
        choices=[
            ('reclamo', 'Reclamo'),
            ('consulta', 'Consulta'),
        ]
    )

    # Comentario inicial del empleado.
    comentario = forms.CharField(
        label='Comentario',
        widget=forms.Textarea(attrs={'rows': 5})
    )