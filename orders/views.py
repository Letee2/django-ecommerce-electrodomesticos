from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem
from cart.models import CartItem
from decimal import Decimal
from django.contrib.admin.views.decorators import user_passes_test
from django.views.decorators.http import require_POST
from cart.cart import Cart
from .notifications import send_order_confirmation_email, send_order_status_email
from django.http import JsonResponse

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
def create_order(request, payment_method, shipping_method):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
    else:
        cart = get_or_create_cart(request)
        cart_items = CartItem.objects.filter(cart=cart)

    if not cart_items.exists():
        return None

    # Verificar stock disponible
    for cart_item in cart_items:
        if cart_item.quantity > cart_item.product.stock:
            return None

    # Calcular costos
    shipping_cost = Decimal('4.99') if shipping_method == 'express' else Decimal('0')
    subtotal = sum(
        item.quantity * (item.product.precio_promocion if item.product.en_promocion else item.product.precio)
        for item in cart_items
    )
    total = subtotal + shipping_cost

    # Crear el pedido
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        shipping_method=shipping_method,
        payment_method=payment_method,
        shipping_cost=shipping_cost,
        total=total
    )

    # Crear los items del pedido y actualizar stock
    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            price=cart_item.product.precio_promocion if cart_item.product.en_promocion else cart_item.product.precio
        )
        cart_item.product.stock -= cart_item.quantity
        cart_item.product.save()

    # Enviar correo de confirmación
    if request.user.is_authenticated:
        send_order_confirmation_email(order)
        send_order_status_email(order)

    return order

@user_passes_test(lambda u: u.is_staff)
def update_order_status(request, order_id):
    if request.method == 'POST':
        order = Order.objects.get(id=order_id)
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            
            # Enviar email de notificación
            from .notifications import send_order_status_email
            send_order_status_email(order)
            
            messages.success(request, 'Estado del pedido actualizado correctamente')
    return redirect('admin_orders')

@login_required
@require_POST
def checkout_cod(request):
    cart = Cart(request)
    if cart:
        order = Order.objects.create(
            user=request.user,
            payment_method='COD',
            status='pending'
        )
        
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price=item['price'],
                quantity=item['quantity']
            )
            
        cart.clear()
        return redirect('order_success')
    return redirect('cart:cart_detail')

@login_required
def payment_success(request):
    try:
        order = Order.objects.filter(user=request.user).latest('created_at')
        
        # Verificar stock disponible
        for item in order.items.all():
            if item.quantity > item.product.stock:
                messages.error(request, f'No hay suficiente stock disponible para {item.product.nombre}')
                return redirect('cart:cart_detail')
        
        # Si hay suficiente stock, procedemos con la actualización
        order.status = 'paid'
        order.save()
        
        # Actualizar el stock de los productos
        for item in order.items.all():
            product = item.product
            product.stock -= item.quantity
            product.save()
        
        # Limpiar el carrito
        CartItem.objects.filter(user=request.user).delete()
        
        return render(request, 'orders/payment_success.html', {
            'order': order,
            'items': order.items.all()
        })
    except Order.DoesNotExist:
        messages.error(request, 'No se encontró el pedido')
        return redirect('home')

@login_required
def get_last_order(request):
    try:
        order = Order.objects.filter(user=request.user).latest('created_at')
        order.status = 'paid'
        order.save()
        
        # Actualizar el stock de los productos
        for item in order.items.all():
            product = item.product
            product.stock -= item.quantity
            product.save()
        
        products = [{
            'name': item.product.nombre,
            'quantity': item.quantity,
            'price': float(item.price * item.quantity)
        } for item in order.items.all()]
        
        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'total': float(order.total),
            'products': products
        })
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'No se encontró el pedido'}) 