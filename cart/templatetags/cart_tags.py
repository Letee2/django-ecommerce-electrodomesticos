from django import template
from cart.models import CartItem

register = template.Library()

@register.filter
def cart_count(user):
    if user.is_authenticated:
        return sum(item.quantity for item in CartItem.objects.filter(user=user))
    return 0