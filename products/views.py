from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .models import Product, Category
from decimal import Decimal
from django.http import JsonResponse

def home(request):
    productos_destacados = Product.objects.filter(destacado=True)
    productos_promocion = Product.objects.filter(en_promocion=True)
    context = {
        'productos_destacados': productos_destacados,
        'productos_promocion': productos_promocion,
    }
    return render(request, 'products/home.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'products/product_detail.html', {'product': product})

def is_staff(user):
    return user.is_staff

@user_passes_test(is_staff)
def admin_panel(request):
    productos = Product.objects.all().order_by('-id')
    context = {
        'productos': productos,
    }
    return render(request, 'products/admin_panel.html', context)

@user_passes_test(lambda u: u.is_staff)
def add_product(request):
    if request.method == 'POST':
        try:
            product = Product.objects.create(
                nombre=request.POST['nombre'],
                descripcion=request.POST['descripcion'],
                precio=request.POST['precio'],
                destacado=request.POST.get('destacado', False),
                en_promocion=request.POST.get('en_promocion', False),
                descuento=request.POST['descuento'],
                stock=request.POST['stock']
            )
            if 'imagen' in request.FILES:
                product.imagen = request.FILES['imagen']
            product.save()
            messages.success(request, 'Producto añadido correctamente')
        except Exception as e:
            messages.error(request, f'Error al añadir el producto: {str(e)}')
        return redirect('admin_panel')

@user_passes_test(lambda u: u.is_staff)
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        try:
            product.nombre = request.POST['nombre']
            product.descripcion = request.POST['descripcion']
            product.precio = Decimal(request.POST['precio'])
            product.destacado = request.POST.get('destacado') == 'on'
            product.en_promocion = request.POST.get('en_promocion') == 'on'
            product.descuento = int(request.POST['descuento'])
            product.stock = int(request.POST['stock'])  # Convertir a entero
            if 'imagen' in request.FILES:
                product.imagen = request.FILES['imagen']
            product.save()
            messages.success(request, 'Producto actualizado correctamente')
        except ValueError as e:
            messages.error(request, 'Error: Asegúrate de introducir valores numéricos válidos')
        except Exception as e:
            messages.error(request, f'Error al actualizar el producto: {str(e)}')
        return redirect('admin_panel')

@user_passes_test(is_staff)
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, 'Producto eliminado correctamente')
    return redirect('admin_panel')

def catalog(request):
    productos = Product.objects.all()
    categorias = Category.objects.all()

    # Filtros avanzados
    categoria = request.GET.get('categoria')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    ordenar = request.GET.get('ordenar')
    solo_promociones = request.GET.get('promociones')
    disponibilidad = request.GET.get('disponibilidad')
    valoracion_min = request.GET.get('valoracion_min')
    busqueda = request.GET.get('busqueda')

    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda)
    
    if categoria:
        productos = productos.filter(categoria__slug=categoria)
    
    if precio_min:
        productos = productos.filter(precio__gte=precio_min)
    
    if precio_max:
        productos = productos.filter(precio__lte=precio_max)
        
    if solo_promociones:
        productos = productos.filter(en_promocion=True)
        
    if disponibilidad == 'disponible':
        productos = productos.filter(stock__gt=0)
    elif disponibilidad == 'agotado':
        productos = productos.filter(stock=0)
        
    if valoracion_min:
        productos = productos.filter(valoracion__gte=valoracion_min)

    if ordenar:
        if ordenar == 'precio_asc':
            productos = productos.order_by('precio')
        elif ordenar == 'precio_desc':
            productos = productos.order_by('-precio')
        elif ordenar == 'mas_comprado':
            productos = productos.order_by('-veces_comprado')
        elif ordenar == 'mejor_valorado':
            productos = productos.order_by('-valoracion')
        elif ordenar == 'descuento':
            productos = productos.filter(en_promocion=True).order_by('-descuento')
        elif ordenar == 'mas_nuevo':
            productos = productos.order_by('-id')

    context = {
        'productos': productos,
        'categorias': categorias,
        'filtros': request.GET,
    }
    return render(request, 'products/catalog.html', context)

def search_products(request):
    query = request.GET.get('query', '')
    productos = Product.objects.filter(nombre__icontains=query)
    
    results = []
    for producto in productos:
        results.append({
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': str(producto.precio),
            'precio_promocion': str(producto.precio_promocion) if producto.en_promocion else None,
            'descuento': producto.descuento if producto.en_promocion else None,
            'imagen_url': producto.imagen.url if producto.imagen else None,
            'stock': producto.stock,
            'en_promocion': producto.en_promocion,
        })
    
    return JsonResponse({'results': results})

def search_products_ajax(request):
    query = request.GET.get('query', '')
    productos = Product.objects.filter(nombre__icontains=query)[:10]  # Limitamos a 8 resultados
    
    results = []
    for producto in productos:
        precio_mostrar = producto.precio_promocion if producto.en_promocion else producto.precio
        results.append({
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': str(precio_mostrar),
            'imagen_url': producto.imagen.url if producto.imagen else None,
            'en_promocion': producto.en_promocion,
            'descuento': producto.descuento if producto.en_promocion else None,
            'url': f'/products/{producto.id}/'
        })
    
    return JsonResponse({'results': results})
