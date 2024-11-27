from django.test import TestCase, Client
from django.urls import reverse
from products.models import Product, Category
from decimal import Decimal

class CatalogViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(
            nombre="Electrodomésticos",
            slug="electrodomesticos"
        )
        
        # Crear productos de prueba
        self.product1 = Product.objects.create(
            nombre="Lavadora Premium",
            precio=Decimal('599.99'),
            categoria=self.category,
            stock=10,
            en_promocion=True,
            descuento=20,
            valoracion=4.5
        )
        
        self.product2 = Product.objects.create(
            nombre="Nevera Básica",
            precio=Decimal('299.99'),
            categoria=self.category,
            stock=5,
            valoracion=3.8
        )

    def test_catalog_basic_view(self):
        """Test de vista básica del catálogo"""
        response = self.client.get(reverse('catalog'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/catalog.html')
        self.assertEqual(len(response.context['productos']), 2)

    def test_catalog_search(self):
        """Test de búsqueda en catálogo"""
        response = self.client.get(reverse('catalog'), {'busqueda': 'Lavadora'})
        self.assertEqual(len(response.context['productos']), 1)
        self.assertEqual(response.context['productos'][0], self.product1)

    def test_catalog_price_filter(self):
        """Test de filtro por precio"""
        response = self.client.get(reverse('catalog'), {
            'precio_min': '400',
            'precio_max': '700'
        })
        self.assertEqual(len(response.context['productos']), 1)
        self.assertEqual(response.context['productos'][0], self.product1)

    def test_catalog_category_filter(self):
        """Test de filtro por categoría"""
        response = self.client.get(reverse('catalog'), {
            'categoria': self.category.slug
        })
        self.assertEqual(len(response.context['productos']), 2)

    def test_catalog_promotion_filter(self):
        """Test de filtro por promociones"""
        response = self.client.get(reverse('catalog'), {'promociones': 'on'})
        self.assertEqual(len(response.context['productos']), 1)
        self.assertTrue(response.context['productos'][0].en_promocion)

    def test_catalog_sorting(self):
        """Test de ordenamiento de productos"""
        # Test ordenar por precio ascendente
        response = self.client.get(reverse('catalog'), {'ordenar': 'precio_asc'})
        productos = list(response.context['productos'])
        self.assertEqual(productos[0], self.product2)
        self.assertEqual(productos[1], self.product1)

        # Test ordenar por valoración
        response = self.client.get(reverse('catalog'), {'ordenar': 'mejor_valorado'})
        productos = list(response.context['productos'])
        self.assertEqual(productos[0], self.product1)
        self.assertEqual(productos[1], self.product2) 