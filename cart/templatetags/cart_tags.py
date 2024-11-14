from django import template
from cart.models import CartItem
from django.db.models import Sum

register = template.Library()

@register.filter(name='cart_item_count')
def cart_item_count(user):
    if user.is_authenticated:
        return CartItem.objects.filter(user=user).aggregate(
            total_items=Sum('quantity'))['total_items'] or 0
    return 0