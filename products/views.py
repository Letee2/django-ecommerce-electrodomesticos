from django.shortcuts import render, get_object_or_404
from .models import Product

def home(request):
    productos_destacados = Product.objects.filter(destacado=True)
    promociones = Product.objects.filter(promocion=True)
    context = {
        'productos_destacados': productos_destacados,
        'promociones': promociones,
    }
    return render(request, 'products/home.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'products/product_detail.html', {'product': product})

def catalog(request):
    products = Product.objects.all()
    hay_promociones = products.filter(promocion=True).exists()
    return render(request, 'products/catalog.html', {
        'products': products,
        'hay_promociones': hay_promociones
    })
