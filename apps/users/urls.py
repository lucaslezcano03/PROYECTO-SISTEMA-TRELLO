from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('', views.inicio_por_rol, name='inicio_por_rol'),
    path('registro/', views.registro_empleado, name='registro_empleado'),
]