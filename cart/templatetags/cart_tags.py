from django import template
from cart.cart import Cart
from cart.models import CartItem

register = template.Library()

@register.filter
def cart_count(request):
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        return sum(item.quantity for item in cart_items)
    else:
        return request.session.get('cart_count', 0)

@register.filter
def multiply(value, arg):
    return float(value) * float(arg)

@register.filter
def subtotal(cart_item):
    if cart_item.product.en_promocion:
        return cart_item.quantity * cart_item.product.precio_promocion
    return cart_item.quantity * cart_item.product.precio