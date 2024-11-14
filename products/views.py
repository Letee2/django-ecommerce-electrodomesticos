from django.shortcuts import render
from .models import Product

def home(request):
    productos_destacados = Product.objects.filter(destacado=True)
    promociones = Product.objects.filter(promocion=True)
    context = {
        'productos_destacados': productos_destacados,
        'promociones': promociones,
    }
    return render(request, 'products/home.html', context)
