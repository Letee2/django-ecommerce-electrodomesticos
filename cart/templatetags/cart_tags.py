from django import template
from cart.models import CartItem

register = template.Library()

@register.filter
def cart_count(user_or_session_key):
    # Si es un usuario autenticado
    if hasattr(user_or_session_key, 'is_authenticated') and user_or_session_key.is_authenticated:
        return CartItem.objects.filter(user=user_or_session_key).count()
    # Si es una session_key (cadena)
    elif isinstance(user_or_session_key, str):
        return CartItem.objects.filter(session_key=user_or_session_key).count()
    # Si no es válido, retorna 0
    return 0
