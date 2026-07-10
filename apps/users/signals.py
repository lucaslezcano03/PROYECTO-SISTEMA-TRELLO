from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    # Cada vez que se crea un usuario, también se crea su perfil.
    if created:
        UserProfile.objects.create(usuario=instance)