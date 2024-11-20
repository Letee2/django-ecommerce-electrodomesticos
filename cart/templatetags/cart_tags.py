from django import template
from cart.models import CartItem

register = template.Library()

@register.simple_tag
def cart_item_count(user):
    if user.is_authenticated:
        return CartItem.objects.filter(user=user).count()
    return 0