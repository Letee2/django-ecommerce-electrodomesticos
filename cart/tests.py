from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from products.models import Product
from .models import CartItem
from decimal import Decimal
import json

class CartTestCase(TestCase):
    def setUp(self):
        # Configurar el cliente de pruebas
        self.client = Client()

        # Crear un usuario de prueba
        self.user = User.objects.create_user(username='testuser', password='password123')

        # Crear un producto de prueba
        self.product = Product.objects.create(
            nombre='Test Product',
            descripcion='Test Description',
            precio=Decimal('100.00'),
            stock=10,
            en_promocion=False,
            precio_promocion=Decimal('90.00')
        )

        # Loguear al cliente de prueba
        self.client.login(username='testuser', password='password123')

    def test_add_to_cart(self):
        """
        Prueba para agregar un producto al carrito.
        """
        response = self.client.post(reverse('add_to_cart', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)  # Verifica que la respuesta sea exitosa
        self.assertEqual(CartItem.objects.count(), 1)  # Verifica que se haya creado un CartItem
        cart_item = CartItem.objects.first()
        self.assertEqual(cart_item.quantity, 1)  # Verifica que la cantidad sea 1
        self.assertEqual(cart_item.product, self.product)  # Verifica que sea el producto correcto

    def test_remove_from_cart(self):
        """
        Prueba para eliminar un producto del carrito.
        """
        cart_item = CartItem.objects.create(user=self.user, product=self.product, quantity=2)
        response = self.client.post(reverse('remove_from_cart', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)  # Verifica que la respuesta sea exitosa
        self.assertEqual(CartItem.objects.count(), 0)  # Verifica que se haya eliminado el CartItem

    def test_checkout_cart_empty(self):
        """
        Prueba para intentar un checkout con un carrito vacío.
        """
        response = self.client.post(reverse('checkout_cod'), follow=True)  # Sigue la redirección
        self.assertRedirects(response, reverse('cart_detail'))  # Verifica la redirección
        self.assertContains(response, 'Tu carrito está vacío', html=True)  # Verifica el mensaje en la página redirigida

    def test_update_quantity_valid(self):
        """
        Prueba para actualizar la cantidad de un producto a un valor válido.
        """
        cart_item = CartItem.objects.create(user=self.user, product=self.product, quantity=2)
        response = self.client.post(
            reverse('update_quantity', args=[self.product.id]),
            data=json.dumps({'quantity': 5}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 5)
        self.assertIn('success', response.json())

    def test_update_quantity_invalid_stock(self):
        """
        Prueba para intentar actualizar la cantidad más allá del stock disponible.
        """
        cart_item = CartItem.objects.create(user=self.user, product=self.product, quantity=2)
        response = self.client.post(
            reverse('update_quantity', args=[self.product.id]),
            data=json.dumps({'quantity': 15}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.json())
        self.assertEqual(response.json()['error'], f'Solo hay {self.product.stock} unidades disponibles')
    def test_create_checkout_session_empty_cart(self):
        """
        Prueba para intentar crear una sesión de pago con el carrito vacío.
        """
        response = self.client.post(reverse('create_checkout_session'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.json())
        self.assertEqual(response.json()['error'], 'El carrito está vacío')

    def test_create_checkout_session_valid(self):
        """
        Prueba para crear una sesión de pago con un carrito lleno.
        """
        CartItem.objects.create(user=self.user, product=self.product, quantity=2)
        response = self.client.post(reverse('create_checkout_session'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.json())
