from django import template
from cart.cart import Cart

register = template.Library()

@register.filter
def cart_count(request):
    cart = Cart(request)
    return len(cart)

@register.filter
def multiply(value, arg):
    return float(value) * float(arg)

@register.filter
def subtotal(cart_item):
    if cart_item.product.en_promocion:
        return cart_item.quantity * cart_item.product.precio_promocion
    return cart_item.quantity * cart_item.product.precio