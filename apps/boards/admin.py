from django.contrib import admin
from .models import Board, BoardColumn


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'creado_por', 'fecha_creacion')
    search_fields = ('nombre', 'descripcion')


@admin.register(BoardColumn)
class BoardColumnAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tablero', 'posicion')
    list_filter = ('tablero',)
