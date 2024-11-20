from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    direccion_envio = models.CharField(max_length=200, blank=True)
    ciudad_envio = models.CharField(max_length=100, blank=True)
    codigo_postal_envio = models.CharField(max_length=10, blank=True)
    direccion_facturacion = models.CharField(max_length=200, blank=True)
    ciudad_facturacion = models.CharField(max_length=100, blank=True)
    codigo_postal_facturacion = models.CharField(max_length=10, blank=True)
    telefono = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
