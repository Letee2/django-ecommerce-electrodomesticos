from django.db import models

class Product(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/')
    destacado = models.BooleanField(default=False)
    promocion = models.BooleanField(default=False)
    descuento = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def precio_con_descuento(self):
        if self.promocion:
            descuento = self.precio * (self.descuento / 100)
            return self.precio - descuento
        return self.precio

    def __str__(self):
        return self.nombre