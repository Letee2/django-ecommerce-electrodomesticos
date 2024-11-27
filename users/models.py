from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=15, blank=True)
    
    # Dirección de envío
    direccion_envio = models.CharField(max_length=200, blank=True)
    ciudad_envio = models.CharField(max_length=100, blank=True)
    codigo_postal_envio = models.CharField(max_length=10, blank=True)
    
    # Dirección de facturación
    direccion_facturacion = models.CharField(max_length=200, blank=True)
    ciudad_facturacion = models.CharField(max_length=100, blank=True)
    codigo_postal_facturacion = models.CharField(max_length=10, blank=True)
    
    # Campo para controlar si las direcciones son las mismas
    misma_direccion = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.misma_direccion:
            # Copiar datos de envío a facturación
            self.direccion_facturacion = self.direccion_envio
            self.ciudad_facturacion = self.ciudad_envio
            self.codigo_postal_facturacion = self.codigo_postal_envio
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Perfil de {self.user.username}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
