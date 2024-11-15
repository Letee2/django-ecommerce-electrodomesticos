from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def subtract(value, arg):
    try:
        return Decimal(str(value)) - Decimal(str(arg))
    except:
        return 0
