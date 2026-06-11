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
from django.views.generic import RedirectView


urlpatterns = [
    # Panel administrativo de Django.
    path('admin/', admin.site.urls),

    # Login/logout propios de Django.
    path('accounts/', include('django.contrib.auth.urls')),

    # La página principal redirige al tablero de gestión de reclamos.
    path('', RedirectView.as_view(
        pattern_name='tickets:gestion_reclamos',
        permanent=False
    ), name='inicio'),

    # Rutas de tableros antiguos, se dejan separadas para no mezclar con la gestión real.
    path('tableros/', include('apps.boards.urls')),

    # Rutas principales de tickets y reclamos.
    path('tickets/', include('apps.tickets.urls')),

    # Rutas principales de notificaciones
    path('notificaciones/', include('apps.notifications.urls')),
]