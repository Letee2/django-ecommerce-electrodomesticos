from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from django.utils import timezone

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)
    
    def get_total(self):
        return self.product.precio_con_descuento() * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.nombre}"
