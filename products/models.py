from django.db import models
from decimal import Decimal
from django.core.exceptions import ValidationError

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
    #categoria = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    categoria = models.ForeignKey(Category, on_delete=models.CASCADE)
    valoracion = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    num_valoraciones = models.PositiveIntegerField(default=0)
    veces_comprado = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.en_promocion and self.descuento > 0:
            precio_con_descuento = self.precio * (Decimal('1') - Decimal(str(self.descuento))/Decimal('100'))
            self.precio_promocion = Decimal(str(round(precio_con_descuento, 2)))
        else:
            self.precio_promocion = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre
        
    @property
    def agotado(self):
        return self.stock <= 0

    def clean(self):
        if self.precio is not None and self.precio < 0:
            raise ValidationError('El precio no puede ser negativo')
        if self.stock is not None and self.stock < 0:
            raise ValidationError('El stock no puede ser negativo')
        if self.descuento is not None and (self.descuento < 0 or self.descuento > 100):
            raise ValidationError('El descuento debe estar entre 0 y 100')
        super().clean()