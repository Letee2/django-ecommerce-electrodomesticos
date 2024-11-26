from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db import transaction
from .models import CartItem, Cart
from products.models import Product
from users.models import UserProfile
from orders.views import create_order
import stripe
from django.conf import settings
from django.http import JsonResponse
from decimal import Decimal
import json
stripe.api_key = settings.STRIPE_SECRET_KEY

def cart_detail(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
    else:
        cart = get_or_create_cart(request)
        cart_items = CartItem.objects.filter(cart=cart)
    
    total = sum(
        item.quantity * (item.product.precio_promocion if item.product.en_promocion else item.product.precio)
        for item in cart_items
    )
    context = {
        'cart_items': cart_items,
        'total': total,
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY
    }
    return render(request, 'cart/cart_detail.html', context)

def get_or_create_cart(request):
    cart_id = request.session.get('cart_id')
    if cart_id:
        cart = Cart.objects.filter(id=cart_id).first()
        if cart:
            return cart
    cart = Cart.objects.create()
    request.session['cart_id'] = cart.id
    return cart

def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = Product.objects.get(id=product_id)
        if request.user.is_authenticated:
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product=product
            )
        else:
            cart = get_or_create_cart(request)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product
            )
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        
        cart_count = get_cart_count(request)
        return JsonResponse({
            'success': True,
            'cart_count': cart_count
        })
    return JsonResponse({'success': False})

def get_cart_count(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
    else:
        cart = get_or_create_cart(request)
        cart_items = CartItem.objects.filter(cart=cart)
    return sum(item.quantity for item in cart_items)

def checkout_cod(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            if request.user.is_authenticated:
                cart_items = CartItem.objects.filter(user=request.user)
            else:
                cart = get_or_create_cart(request)
                cart_items = CartItem.objects.filter(cart=cart)

            if not cart_items.exists():
                return JsonResponse({'error': 'El carrito está vacío'})

            shipping_method = data.get('shipping_method', 'free')
            shipping_cost = 499 if shipping_method == 'express' else 0

            # Crear la orden
            order = create_order(request, payment_method='cod', shipping_method=shipping_method)
            
            if order:
                # Preparar datos de productos para el modal
                products = [{
                    'name': item.product.nombre,
                    'quantity': item.quantity,
                    'price': float(item.quantity * (item.product.precio_promocion if item.product.en_promocion else item.product.precio))
                } for item in cart_items]
                
                total = sum(item['price'] for item in products)
                if shipping_method == 'express':
                    total += shipping_cost

                # Limpiar el carrito
                cart_items.delete()
                
                return JsonResponse({
                    'success': True,
                    'order_id': order.id,
                    'products': products,
                    'total': total,
                    'redirect_url': reverse('cart:payment_success')
                })
            else:
                return JsonResponse({'error': 'Error al crear el pedido'})

        except Exception as e:
            return JsonResponse({'error': str(e)})

    return JsonResponse({'error': 'Método no permitido'}, status=405)

def create_checkout_session(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            if request.user.is_authenticated:
                profile = request.user.userprofile
                if not all([profile.direccion_envio, profile.ciudad_envio, 
                           profile.codigo_postal_envio, profile.telefono]):
                    return JsonResponse({
                        'incomplete_profile': True,
                        'error': 'Por favor, completa todos los datos de envío necesarios'
                    })
                
                # Usar datos del perfil
                data.update({
                    'nombre': request.user.get_full_name() or request.user.username,
                    'email': request.user.email,
                    'direccion_envio': profile.direccion_envio,
                    'ciudad_envio': profile.ciudad_envio,
                    'codigo_postal_envio': profile.codigo_postal_envio,
                    'telefono': profile.telefono  # Cambiado de telefono_envio a telefono
                })
            else:
                # Validar datos para usuarios no autenticados
                required_fields = ['nombre', 'email', 'direccion_envio', 'ciudad_envio', 'codigo_postal_envio', 'telefono', 'password']
                for field in required_fields:
                    if not data.get(field):
                        return JsonResponse({'error': f'El campo {field} es obligatorio'})

            # Si el usuario no está autenticado, creamos una cuenta
            if not request.user.is_authenticated:
                with transaction.atomic():
                    try:
                        # Verificar si el usuario ya existe
                        if User.objects.filter(email=data['email']).exists():
                            return JsonResponse({
                                'error': 'Ya existe una cuenta con este email. Por favor, inicia sesión.'
                            })

                        # Crear usuario
                        user = User.objects.create_user(
                            username=data['email'],
                            email=data['email'],
                            password=data['password'],
                            first_name=data['nombre']
                        )
                        
                        # Mapear los datos del formulario a los campos del modelo
                        profile_data = {
                            'telefono_envio': data['telefono'],
                            'direccion_envio': data['direccion_envio'],
                            'ciudad_envio': data['ciudad_envio'],
                            'codigo_postal_envio': data['codigo_postal_envio']
                        }
                        
                        # Crear perfil
                        UserProfile.objects.create(
                            user=user,
                            **profile_data
                        )
                        
                        # Iniciar sesión
                        login(request, user)
                        
                        # Transferir items del carrito anónimo al usuario
                        cart = get_or_create_cart(request)
                        CartItem.objects.filter(cart=cart).update(user=user, cart=None)
                    except Exception as e:
                        return JsonResponse({'error': str(e)})

            # Crear las líneas de pedido para Stripe
            line_items = []
            cart_items = CartItem.objects.filter(user=request.user) if request.user.is_authenticated else CartItem.objects.filter(cart=get_or_create_cart(request))

            if not cart_items.exists():
                return JsonResponse({'error': 'El carrito está vacío'})

            # Guardar datos de envío en sesión
            shipping_data = {
                'nombre': data['nombre'],
                'email': data['email'],
                'direccion': data['direccion_envio'],
                'ciudad': data['ciudad_envio'],
                'codigo_postal': data['codigo_postal_envio'],
                'telefono': data['telefono']
            }
            request.session['shipping_data'] = shipping_data

            # Calcular costos de envío
            shipping_method = data.get('shipping_method', 'free')
            shipping_cost = 499 if shipping_method == 'express' else 0

            try:
                # Crear las líneas de pedido dinámicamente con precios del modelo
                for item in cart_items:
                    # Determinar el precio (promoción o normal)
                    unit_price = (
                        item.product.precio_promocion if item.product.en_promocion else item.product.precio
                    )
                    
                    line_items.append({
                        'price_data': {
                            'currency': 'eur',
                            'product_data': {
                                'name': item.product.nombre,
                                'description': item.product.descripcion,  # Opcional
                            },
                            'unit_amount': int(unit_price * 100),  # Convertir a centavos
                        },
                        'quantity': item.quantity,
                    })

                # Agregar costos de envío como línea separada
                if shipping_cost > 0:
                    line_items.append({
                        'price_data': {
                            'currency': 'eur',
                            'product_data': {
                                'name': 'Envío rápido',
                            },
                            'unit_amount': shipping_cost,
                        },
                        'quantity': 1,
                    })

                # Crear la sesión de pago en Stripe
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=line_items,
                    mode='payment',
                    success_url=request.build_absolute_uri('/payment/success/'),
                    cancel_url=request.build_absolute_uri('/cart/'),
                )

                return JsonResponse({'id': checkout_session.id})
            except Exception as e:
                return JsonResponse({'error': str(e)})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'})
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


def checkout_success(request):
    if request.user.is_authenticated:
        CartItem.objects.filter(user=request.user).delete()
    else:
        session_key = request.session.session_key
        if session_key:
            CartItem.objects.filter(session_key=session_key).delete()

    messages.success(request, '¡Pago realizado con éxito! Gracias por tu compra.')
    return redirect('home')

def payment_success(request):
    if request.user.is_authenticated:
        CartItem.objects.filter(user=request.user).delete()
    else:
        session_key = request.session.session_key
        if session_key:
            CartItem.objects.filter(session_key=session_key).delete()

    messages.success(request, '¡Pago realizado con éxito! Gracias por tu compra.')
    return redirect('home')

def remove_from_cart(request, product_id):
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, id=product_id)
            if request.user.is_authenticated:
                cart_item = CartItem.objects.filter(user=request.user, product=product)
            else:
                cart = get_or_create_cart(request)
                cart_item = CartItem.objects.filter(cart=cart, product=product)
            
            cart_item.delete()
            
            # Calcular nuevos totales
            if request.user.is_authenticated:
                cart_items = CartItem.objects.filter(user=request.user)
            else:
                cart_items = CartItem.objects.filter(cart=cart)
            
            cart_count = sum(item.quantity for item in cart_items)
            total = sum(
                item.quantity * (item.product.precio_promocion if item.product.en_promocion else item.product.precio)
                for item in cart_items
            )
            
            return JsonResponse({
                'success': True,
                'cart_count': cart_count,
                'total': float(total)
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})

def update_quantity(request, product_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_quantity = int(data.get('quantity', 0))

            if new_quantity < 1:
                return JsonResponse({
                    'success': False,
                    'error': 'La cantidad debe ser al menos 1'
                })
            
            if request.user.is_authenticated:
                cart_item = CartItem.objects.get(user=request.user, product_id=product_id)
            else:
                cart = get_or_create_cart(request)
                cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            
            if new_quantity > cart_item.product.stock:
                return JsonResponse({
                    'success': False,
                    'error': f'Solo hay {cart_item.product.stock} unidades disponibles'
                })
            
            cart_item.quantity = new_quantity
            cart_item.save()
            
            # Calcular nuevos totales
            if request.user.is_authenticated:
                cart_items = CartItem.objects.filter(user=request.user)
            else:
                cart_items = CartItem.objects.filter(cart=cart)
                
            cart_count = sum(item.quantity for item in cart_items)
            total = sum(
                item.quantity * (item.product.precio_promocion if item.product.en_promocion else item.product.precio)
                for item in cart_items
            )

            return JsonResponse({
                'success': True,
                'cart_count': cart_count,
                'total': float(total),
                'item_total': float(cart_item.quantity * (cart_item.product.precio_promocion if cart_item.product.en_promocion else cart_item.product.precio))
            })
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Producto no encontrado en el carrito'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def update_cart_item(request, product_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))
            
            # Obtener o crear el carrito
            cart, _ = Cart.objects.get_or_create(user=request.user)
            product = get_object_or_404(Product, id=product_id)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            
            # Actualizar cantidad
            cart_item.quantity = quantity
            cart_item.save()
            
            # Calcular totales
            cart_count = cart.get_total_items()
            total = cart.get_total_price()
            
            return JsonResponse({
                'success': True,
                'cart_count': cart_count,
                'total': float(total),
                'item_total': float(cart_item.get_total())
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False})
