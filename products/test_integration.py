from django.test import TestCase, Client
from django.urls import reverse
from products.models import Product, Category
from users.models import UserProfile
from django.contrib.auth.models import User
from cart.models import Cart, CartItem
from decimal import Decimal
import uuid

class ProductIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Generar username único
        unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
        self.user = User.objects.create_user(
            username=unique_username,
            password='testpass123',
            email=f'{unique_username}@example.com'
        )
        
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

    '''def test_add_to_cart_flow(self):
        # Asegurarnos de que el usuario está autenticado
        self.client.force_login(self.user)
        
        # Añadir al carrito
        response = self.client.post(
            reverse('cart:add_to_cart', args=[self.product.id]),
            {'quantity': 1}
        )
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el producto está en el carrito
        cart_items = CartItem.objects.filter(user=self.user)
        self.assertEqual(cart_items.count(), 1)
        self.assertEqual(cart_items[0].product, self.product)'''

    def test_product_search_and_filter(self):
        response = self.client.get(
            reverse('catalog'),
            {'busqueda': 'Lavadora', 'categoria': self.category.slug}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lavadora Test')

    def test_promotion_price_calculation(self):
        self.client.force_login(self.user)
        cart = Cart.objects.create()
        
        cart_item = CartItem.objects.create(
            user=self.user,
            product=self.product,
            quantity=1
        )
        
        # Activar promoción
        self.product.en_promocion = True
        self.product.descuento = 20
        self.product.save()
        
        # Añadir al carrito
        self.client.login(username='testuser', password='testpass123')
        self.client.post(
            reverse('cart:add_to_cart', args=[self.product.id]),
            {'quantity': 1}
        )
        
        # Verificar precio en carrito
        cart_item = CartItem.objects.get(user=self.user, product=self.product)
        expected_price = Decimal('399.99')  # 499.99 - 20%
        self.assertEqual(cart_item.get_price(), expected_price) 

    '''def test_product_stock_management(self):
        self.client.force_login(self.user)
        
        # Intentar añadir más que el stock disponible
        response = self.client.post(
            reverse('cart:add_to_cart', args=[self.product.id]),
            {'quantity': self.product.stock + 1},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'  # Para indicar que es una petición AJAX
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())'''

    def test_product_price_changes(self):
        self.client.force_login(self.user)
        
        # Crear CartItem
        cart_item = CartItem.objects.create(
            user=self.user,
            product=self.product,
            quantity=1
        )
        
        precio_inicial = cart_item.get_price()
        
        # Activar promoción
        self.product.en_promocion = True
        self.product.descuento = 20
        self.product.save()
        
        # Verificar que el precio se actualiza
        cart_item.refresh_from_db()
        self.assertNotEqual(cart_item.get_price(), precio_inicial)
        self.assertEqual(cart_item.get_price(), self.product.precio_promocion)

class ProductCategoryIntegrationTest(TestCase):
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

    def test_category_deletion_cascade(self):
        """Test que verifica el borrado en cascada al eliminar una categoría"""
        product_id = self.product.id
        self.category.delete()
        self.assertFalse(Product.objects.filter(id=product_id).exists())

    def test_category_products_relation(self):
        """Test que verifica la relación bidireccional entre categoría y productos"""
        # Verificar productos desde la categoría
        self.assertEqual(self.category.product_set.count(), 1)
        self.assertEqual(self.category.product_set.first(), self.product)
        
        # Verificar categoría desde el producto
        self.assertEqual(self.product.categoria, self.category)

    def test_multiple_products_in_category(self):
        """Test que verifica múltiples productos en una categoría"""
        Product.objects.create(
            nombre="Nevera Test",
            descripcion="Una nevera de prueba",
            precio=Decimal('899.99'),
            categoria=self.category,
            stock=5
        )
        
        Product.objects.create(
            nombre="Microondas Test",
            descripcion="Un microondas de prueba",
            precio=Decimal('199.99'),
            categoria=self.category,
            stock=15
        )
        
        self.assertEqual(self.category.product_set.count(), 3)

    def test_category_products_stock_total(self):
        """Test que verifica el stock total de productos en una categoría"""
        Product.objects.create(
            nombre="Nevera Test",
            descripcion="Una nevera de prueba",
            precio=Decimal('899.99'),
            categoria=self.category,
            stock=5
        )
        
        total_stock = sum(product.stock for product in self.category.product_set.all())
        self.assertEqual(total_stock, 15)  # 10 + 5

    def test_category_products_promotion(self):
        """Test que verifica productos en promoción por categoría"""
        Product.objects.create(
            nombre="Nevera Test",
            descripcion="Una nevera de prueba",
            precio=Decimal('899.99'),
            categoria=self.category,
            stock=5,
            en_promocion=True,
            descuento=10
        )
        
        productos_promocion = self.category.product_set.filter(en_promocion=True)
        self.assertEqual(productos_promocion.count(), 1)