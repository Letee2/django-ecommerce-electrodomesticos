from django.test import TestCase
from django.core.exceptions import ValidationError
from products.models import Product, Category
from decimal import Decimal

class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            nombre="Electrodomésticos",
            slug="electrodomesticos"
        )
        self.product = Product.objects.create(
            nombre="Lavadora Test",
            descripcion="Una lavadora de prueba",
            precio=Decimal('499.99'),
            categoria=self.category,
            stock=10
        )

    def test_precio_promocion_calculation(self):
        """Test del cálculo correcto del precio promocional"""
        self.product.en_promocion = True
        self.product.descuento = 20
        self.product.save()
        expected_price = Decimal('399.99')
        self.assertEqual(self.product.precio_promocion, expected_price)

    def test_agotado_property(self):
        """Test de la propiedad agotado"""
        self.assertFalse(self.product.agotado)
        self.product.stock = 0
        self.assertTrue(self.product.agotado)

    def test_invalid_price(self):
        """Test de validación de precio negativo"""
        product = Product(
            nombre="Producto Inválido",
            descripcion="Test",
            precio=Decimal('-10.00'),
            categoria=self.category,
            stock=1
        )
        try:
            product.full_clean()
            product.save()
            self.fail("Debería haber lanzado ValidationError")
        except ValidationError:
            pass

    def test_invalid_discount(self):
        """Test de descuento inválido"""
        self.product.descuento = 101
        with self.assertRaises(ValidationError):
            self.product.full_clean()

    def test_stock_validation(self):
        """Test de validación de stock negativo"""
        product = Product(
            nombre="Stock Negativo",
            descripcion="Test",
            precio=Decimal('99.99'),
            stock=-1,
            categoria=self.category
        )
        try:
            product.full_clean()
            product.save()
            self.fail("Debería haber lanzado ValidationError")
        except ValidationError:
            pass 