from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CartItem, Order, OrderItem, PaymentInfo
from products.models import Product

from django.conf import settings
from django.http import JsonResponse
import stripe
import json
import uuid
from django.urls import reverse
import re
from django.db import transaction
from django.views.decorators.http import require_http_methods

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def cart_detail(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.get_total() for item in cart_items)
    context = {
        'cart_items': cart_items,
        'total': total,
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY
    }
    return render(request, 'cart/cart_detail.html', context)

@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, 'Producto añadido al carrito.')
    return redirect('home')

@login_required
def checkout_cod(request):
    if request.method == 'POST':
        cart_items = CartItem.objects.filter(user=request.user)
        # Procesar pedido contrareembolso
        cart_items.delete()
        messages.success(request, 'Pedido realizado correctamente. Pagarás al recibir.')
        return redirect('home')

@login_required
def create_checkout_session(request):
    if request.method == 'POST':
        cart_items = CartItem.objects.filter(user=request.user)
        
        if not cart_items.exists():
            return JsonResponse({'error': 'El carrito está vacío'})

        try:
            # Crear el pedido
            total = sum(item.get_total() for item in cart_items)
            order = Order.objects.create(
                user=request.user,
                total=total,
                payment_method='CARD'
            )
            
            # Crear los items del pedido
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.precio_con_descuento()
                )

            try:
                # Intentar crear sesión de Stripe
                line_items = []
                for item in cart_items:
                    precio = item.product.precio_con_descuento()
                    line_items.append({
                        'price_data': {
                            'currency': 'eur',
                            'product_data': {
                                'name': item.product.nombre,
                                'description': item.product.descripcion[:100],
                            },
                            'unit_amount': int(float(precio) * 100),
                        },
                        'quantity': item.quantity,
                    })

                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=line_items,
                    mode='payment',
                    success_url=request.build_absolute_uri(f'/payment/success/{order.id}/'),
                    cancel_url=request.build_absolute_uri('/cart/'),
                    metadata={
                        'order_id': str(order.id)
                    }
                )
                return JsonResponse({'id': checkout_session.id})
            except Exception as e:
                # Si falla Stripe, redirigir a página de confirmación alternativa
                return JsonResponse({
                    'error': 'Stripe no disponible',
                    'redirect': f'/payment/alternative/{order.id}/'
                })

        except Exception as e:
            return JsonResponse({'error': str(e)})
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def checkout_success(request):
    # Limpiar el carrito después del pago exitoso
    CartItem.objects.filter(user=request.user).delete()
    messages.success(request, '¡Pago realizado con éxito! Gracias por tu compra.')
    return redirect('home')

@require_http_methods(["POST"])
@login_required
def process_payment(request):
    try:
        # Verificar el tipo de contenido
        if request.content_type != 'application/json':
            return JsonResponse({
                'success': False,
                'error': 'Tipo de contenido no válido'
            }, status=400)

        # Decodificar JSON
        data = json.loads(request.body)
        cart_items = CartItem.objects.filter(user=request.user)
        
        if not cart_items.exists():
            return JsonResponse({
                'success': False,
                'error': 'El carrito está vacío'
            }, status=400)

        with transaction.atomic():
            # Crear orden
            total = sum(item.get_total() for item in cart_items)
            order = Order.objects.create(
                user=request.user,
                total=total,
                payment_method='CARD'
            )

            # Crear items de la orden
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.precio_con_descuento()
                )

            # Guardar información de pago
            PaymentInfo.objects.create(
                order=order,
                card_holder=data.get('card_holder', ''),
                card_last_four=data.get('card_number', '')[-4:],
                card_expiry=data.get('card_expiry', ''),
                transaction_id=f"TRX-{uuid.uuid4().hex[:8].upper()}",
                payment_status='COMPLETED'
            )

            # Limpiar carrito
            cart_items.delete()

            return JsonResponse({
                'success': True,
                'redirect_url': '/cart/payment/success/'
            })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Datos JSON no válidos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
def validate_payment(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Validar campos requeridos
        required_fields = ['card_holder', 'card_number', 'card_expiry', 'card_cvc']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error': f'El campo {field} es requerido'}, status=400)
        
        # Validar número de tarjeta (16 dígitos)
        if not re.match(r'^\d{16}$', data['card_number']):
            return JsonResponse({'error': 'Número de tarjeta inválido'}, status=400)
        
        # Validar fecha de expiración (MM/YY)
        if not re.match(r'^(0[1-9]|1[0-2])\/([0-9]{2})$', data['card_expiry']):
            return JsonResponse({'error': 'Fecha de expiración inválida'}, status=400)
        
        # Validar CVC (3-4 dígitos)
        if not re.match(r'^\d{3,4}$', data['card_cvc']):
            return JsonResponse({'error': 'CVC inválido'}, status=400)
        
        return JsonResponse({'success': True})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
