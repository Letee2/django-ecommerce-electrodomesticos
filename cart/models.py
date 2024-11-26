from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from django.core.exceptions import ValidationError

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('user', 'session_key', 'product')  # Evitar duplicados

    def __str__(self):
        return f'{self.quantity}x {self.product.nombre}'

    def get_total(self):
        return self.product.precio * self.quantity

    def clean(self):
        if self.quantity > self.product.stock:
            raise ValidationError(f'Solo hay {self.product.stock} unidades disponibles')
        if self.quantity < 1:
            raise ValidationError('La cantidad debe ser al menos 1')
        if not self.user and not self.session_key:
            raise ValidationError('Debe estar asociado a un usuario o a una sesión.')
