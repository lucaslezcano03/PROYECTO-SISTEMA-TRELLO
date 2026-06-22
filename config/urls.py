"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from apps.tickets import views as ticket_views


urlpatterns = [
    # Panel administrativo de Django.
    path('admin/', admin.site.urls),

    # Login y logout propios de Django.
    path('accounts/', include('django.contrib.auth.urls')),

    # Inicio del sistema, redirige según el rol.
    path('', include('apps.users.urls')),

    # Tableros antiguos o auxiliares.
    path('tableros/', include('apps.boards.urls')),

    # Reclamos y tickets.
    path('tickets/', include('apps.tickets.urls')),

    # Notificaciones.
    path('notificaciones/', include('apps.notifications.urls')),

    # API de tickets para probar desde Postman, navegador o terminal.
    path('api/tickets/', ticket_views.api_tickets, name='api_tickets'),
    path('api/tickets/<int:ticket_id>/', ticket_views.api_ticket_detail, name='api_ticket_detail'),
    path('api/estado/', ticket_views.api_estado_sistema, name='api_estado_sistema'),
]