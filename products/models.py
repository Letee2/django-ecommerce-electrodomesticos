from django.db import models
from decimal import Decimal

class Category(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Categories"

class Product(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/')
    destacado = models.BooleanField(default=False)
    en_promocion = models.BooleanField(default=False)
    descuento = models.IntegerField(default=0)
    precio_promocion = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    categoria = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    valoracion = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    num_valoraciones = models.PositiveIntegerField(default=0)
    veces_comprado = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.en_promocion and self.descuento > 0:
            self.precio_promocion = self.precio * (Decimal('1') - Decimal(str(self.descuento))/Decimal('100'))
        else:
            self.precio_promocion = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre
        
    @property
    def agotado(self):
        return self.stock <= 0