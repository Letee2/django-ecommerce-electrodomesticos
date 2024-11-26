from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from django.core.exceptions import ValidationError

class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Cart {self.id}'

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def get_total(self):
        return self.product.precio * self.quantity

    def clean(self):
        if self.quantity > self.product.stock:
            raise ValidationError(f'Solo hay {self.product.stock} unidades disponibles')
        if self.quantity < 1:
            raise ValidationError('La cantidad debe ser al menos 1')
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(user__isnull=False) & models.Q(cart__isnull=True) |
                    models.Q(user__isnull=True) & models.Q(cart__isnull=False)
                ),
                name='cart_item_user_or_cart'
            )
        ]
