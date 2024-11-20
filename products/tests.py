from django.test import TestCase
from decimal import Decimal
from .models import Product

class ProductModelTest(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            nombre="Lavadora Test",
            descripcion="Una lavadora de prueba",
            precio=Decimal('499.99'),
            destacado=True,
            promocion=True,
            descuento=Decimal('15.00')
        )

    def test_product_creation(self):
        """Test que la creación del producto funciona correctamente"""
        self.assertEqual(self.product.nombre, "Lavadora Test")
        self.assertEqual(self.product.precio, Decimal('499.99'))
        self.assertTrue(self.product.destacado)
        self.assertTrue(self.product.promocion)
        self.assertEqual(self.product.descuento, Decimal('15.00'))

    def test_precio_con_descuento(self):
        """Test que el cálculo del precio con descuento es correcto"""
        precio_esperado = Decimal('499.99') - (Decimal('499.99') * Decimal('0.15'))
        self.assertEqual(self.product.precio_con_descuento(), precio_esperado)

    def test_string_representation(self):
        """Test que la representación en string del producto es correcta"""
        self.assertEqual(str(self.product), "Lavadora Test")

    def test_precio_sin_descuento(self):
        """Test que el precio sin descuento se mantiene cuando no hay promoción"""
        producto_sin_promocion = Product.objects.create(
            nombre="Nevera Test",
            descripcion="Una nevera de prueba",
            precio=Decimal('699.99'),
            promocion=False
        )
        self.assertEqual(producto_sin_promocion.precio_con_descuento(), Decimal('699.99'))
