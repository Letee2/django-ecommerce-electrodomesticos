from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CartItem
from products.models import Product
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
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart_items = CartItem.objects.filter(session_key=session_key)

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



def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = Product.objects.get(id=product_id)

        if request.user.is_authenticated:
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product=product
            )
        else:
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
            cart_item, created = CartItem.objects.get_or_create(
                session_key=session_key,
                product=product
            )

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        cart_count = sum(item.quantity for item in CartItem.objects.filter(
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key if not request.user.is_authenticated else None
        ))

        return JsonResponse({
            'success': True,
            'cart_count': cart_count
        })
    return JsonResponse({'success': False})


def checkout_cod(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            cart_items = CartItem.objects.filter(session_key=session_key)

        if not cart_items.exists():
            messages.error(request, 'Tu carrito está vacío')
            return redirect('cart_detail')

        shipping_method = request.POST.get('shipping_method', 'free')
        return create_order(request, payment_method='cod', shipping_method=shipping_method)


def create_checkout_session(request):
    if request.method == 'POST':
        shipping_method = request.POST.get('shipping_method', 'free')
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            cart_items = CartItem.objects.filter(session_key=session_key)

        if not cart_items.exists():
            return JsonResponse({'error': 'El carrito está vacío'})

        # Calcular costos de envío
        shipping_cost = 499 if shipping_method == 'express' else 0

        try:
            # Crear las líneas de pedido dinámicamente con precios del modelo
            line_items = []
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
        if request.user.is_authenticated:
            CartItem.objects.filter(user=request.user, product_id=product_id).delete()
        else:
            session_key = request.session.session_key
            if session_key:
                CartItem.objects.filter(session_key=session_key, product_id=product_id).delete()

        cart_items = CartItem.objects.filter(
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key if not request.user.is_authenticated else None
        )
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
                session_key = request.session.session_key
                cart_item = CartItem.objects.get(session_key=session_key, product_id=product_id)

            if new_quantity > cart_item.product.stock:
                return JsonResponse({
                    'success': False,
                    'error': f'Solo hay {cart_item.product.stock} unidades disponibles'
                })

            cart_item.quantity = new_quantity
            cart_item.save()

            cart_items = CartItem.objects.filter(
                user=request.user if request.user.is_authenticated else None,
                session_key=request.session.session_key if not request.user.is_authenticated else None
            )
            cart_count = sum(item.quantity for item in cart_items)
            total = sum(
                item.quantity * (item.product.precio_promocion if item.product.en_promocion else item.product.precio)
                for item in cart_items
            )

            return JsonResponse({
                'success': True,
                'cart_count': cart_count,
                'quantity': cart_item.quantity,
                'total': float(total),
                'item_total': float(cart_item.quantity * (cart_item.product.precio_promocion if cart_item.product.en_promocion else cart_item.product.precio))
            })
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Producto no encontrado'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Datos inválidos'})
    return JsonResponse({'success': False})
