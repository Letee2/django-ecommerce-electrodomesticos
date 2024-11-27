from django.test import TestCase
from django.core.exceptions import ValidationError
from products.models import Category

class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            nombre="Electrodomésticos",
            slug="electrodomesticos"
        )

    def test_category_creation(self):
        """Test de creación básica de categoría"""
        self.assertEqual(self.category.nombre, "Electrodomésticos")
        self.assertEqual(self.category.slug, "electrodomesticos")

    def test_duplicate_slug(self):
        """Test de slug duplicado"""
        categoria2 = Category(
            nombre="Electro",
            slug="electrodomesticos"
        )
        try:
            categoria2.full_clean()
            categoria2.save()
            self.fail("Debería haber lanzado ValidationError")
        except ValidationError:
            pass

    def test_category_str(self):
        """Test de representación string"""
        self.assertEqual(str(self.category), "Electrodomésticos")

    def test_empty_name(self):
        """Test de nombre vacío"""
        categoria = Category(
            nombre="",
            slug="vacio"
        )
        with self.assertRaises(ValidationError):
            categoria.full_clean()

    def test_invalid_slug_chars(self):
        """Test de caracteres inválidos en slug"""
        categoria = Category(
            nombre="Test",
            slug="test@invalid"
        )
        with self.assertRaises(ValidationError):
            categoria.full_clean() 