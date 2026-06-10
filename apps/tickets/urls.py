from django.urls import path

from . import views

app_name = 'tickets'

urlpatterns = [
    path('nuevo-reclamo/', views.crear_reclamo_internet, name='crear_reclamo_internet'),
    path('reclamo-enviado/', views.reclamo_enviado, name='reclamo_enviado'),
    path('crear/', views.ticket_create, name='ticket_create'),
    path('<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
]