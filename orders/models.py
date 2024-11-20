from django.db import models
from django.contrib.auth.models import User
from products.models import Product

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('shipped', 'Enviado'),
        ('delivered', 'Entregado'),
    ]
    
    SHIPPING_CHOICES = [
        ('free', 'Envío estándar (3-5 días)'),
        ('express', 'Envío express (24-48h)'),
    ]
    
    PAYMENT_CHOICES = [
        ('card', 'Tarjeta de crédito/débito'),
        ('cod', 'Contrareembolso'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    shipping_method = models.CharField(max_length=10, choices=SHIPPING_CHOICES)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    shipping_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Pedido #{self.id} - {self.user.username}'

    def get_payment_method_display(self):
        return dict(self.PAYMENT_CHOICES)[self.payment_method]

    def get_shipping_method_display(self):
        return dict(self.SHIPPING_CHOICES)[self.shipping_method]

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.quantity}x {self.product.nombre} en Pedido #{self.order.id}'

    @property
    def total(self):
        return self.price * self.quantity 