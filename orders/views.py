from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem
from cart.models import CartItem
from decimal import Decimal
from django.contrib.admin.views.decorators import user_passes_test

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
def create_order(request, payment_method, shipping_method):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        messages.error(request, 'Tu carrito está vacío')
        return redirect('cart_detail')

    # Verificar stock disponible
    for cart_item in cart_items:
        if cart_item.quantity > cart_item.product.stock:
            messages.error(request, f'No hay suficiente stock de {cart_item.product.nombre}')
            return redirect('cart_detail')

    # Calcular costos
    shipping_cost = Decimal('4.99') if shipping_method == 'express' else Decimal('0')
    subtotal = sum(
        item.quantity * (item.product.precio_promocion if item.product.en_promocion else item.product.precio)
        for item in cart_items
    )
    total = subtotal + shipping_cost

    # Crear el pedido
    order = Order.objects.create(
        user=request.user,
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
        # Actualizar stock
        cart_item.product.stock -= cart_item.quantity
        cart_item.product.save()

    # Limpiar el carrito
    cart_items.delete()

    messages.success(request, 'Pedido realizado correctamente')
    return redirect('order_list')

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