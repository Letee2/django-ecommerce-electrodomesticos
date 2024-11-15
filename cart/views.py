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
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def cart_detail(request):
    cart_items = CartItem.objects.filter(user=request.user)
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
        if not cart_items.exists():
            messages.error(request, 'Tu carrito está vacío')
            return redirect('cart_detail')
            
        shipping_method = request.POST.get('shipping_method', 'free')
        return create_order(request, payment_method='cod', shipping_method=shipping_method)

@login_required
def create_checkout_session(request):
    if request.method == 'POST':
        shipping_method = request.POST.get('shipping_method', 'free')
        cart_items = CartItem.objects.filter(user=request.user)
        
        if not cart_items.exists():
            return JsonResponse({'error': 'El carrito está vacío'})

        # Calcular costos de envío
        shipping_cost = 4.99 if shipping_method == 'express' else 0
        
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': item.product.nombre,
                        },
                        'unit_amount': int(item.product.precio * 100),
                    },
                    'quantity': item.quantity,
                } for item in cart_items],
                mode='payment',
                success_url=request.build_absolute_uri('/') + 'payment/success/',
                cancel_url=request.build_absolute_uri('/') + 'cart/',
            )
            return JsonResponse({'id': checkout_session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)})
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def checkout_success(request):
    # Limpiar el carrito después del pago exitoso
    CartItem.objects.filter(user=request.user).delete()
    messages.success(request, '¡Pago realizado con éxito! Gracias por tu compra.')
    return redirect('home')

@login_required
def payment_success(request):
    cart_items = CartItem.objects.filter(user=request.user)
    cart_items.delete()
    messages.success(request, '¡Pago realizado con éxito! Gracias por tu compra.')
    return redirect('home')
