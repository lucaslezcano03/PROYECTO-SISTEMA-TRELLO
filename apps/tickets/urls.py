from django.urls import path

from . import views

app_name = 'tickets'

urlpatterns = [
    path('crear/', views.ticket_create, name='ticket_create'),
    path('<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
]