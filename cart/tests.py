from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from .models import CartItem
from products.models import Product
from django.utils import timezone

class CartItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.product = Product.objects.create(
            nombre="Producto Test",
            descripcion="Descripción de prueba",
            precio=Decimal('100.00')
        )
        self.cart_item = CartItem.objects.create(
            user=self.user,
            product=self.product,
            quantity=2,
            created_at=timezone.now()
        )

    def test_cart_item_creation(self):
        """Test que la creación del item del carrito funciona correctamente"""
        self.assertEqual(self.cart_item.user, self.user)
        self.assertEqual(self.cart_item.product, self.product)
        self.assertEqual(self.cart_item.quantity, 2)

    def test_get_total(self):
        """Test que el cálculo del total del item es correcto"""
        expected_total = Decimal('200.00')  # 100.00 * 2
        self.assertEqual(self.cart_item.get_total(), expected_total)

    def test_get_total_with_promotion(self):
        """Test que el cálculo del total respeta el precio con descuento"""
        self.product.promocion = True
        self.product.descuento = Decimal('20.00')
        self.product.save()
        
        expected_price = Decimal('80.00')  # 100.00 - 20%
        expected_total = expected_price * 2
        self.assertEqual(self.cart_item.get_total(), expected_total)
