from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from django.utils import timezone
from decimal import Decimal

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)
    
    def get_total(self):
        return self.product.precio_con_descuento() * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.nombre}"

class Order(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('PAID', 'Pagado'),
        ('FAILED', 'Fallido')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    payment_method = models.CharField(max_length=20, default='CARD')
    
    def __str__(self):
        return f"Pedido {self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def get_total(self):
        return self.price * self.quantity

class PaymentInfo(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    card_holder = models.CharField(max_length=100)
    # Almacenamos solo los últimos 4 dígitos de la tarjeta por seguridad
    card_last_four = models.CharField(max_length=4)
    card_expiry = models.CharField(max_length=5)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, default='PENDING')
    transaction_id = models.CharField(max_length=100, unique=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['transaction_id']),
        ]
