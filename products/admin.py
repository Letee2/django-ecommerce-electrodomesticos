from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.html import format_html
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'mostrar_imagen', 'precio', 'precio_promocion', 'destacado', 'en_promocion', 'descuento')
    list_filter = ('destacado', 'en_promocion')
    search_fields = ('nombre', 'descripcion')
    readonly_fields = ('precio_promocion', 'preview_imagen')
    
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'nombre',
                'descripcion',
                'precio',
                ('imagen', 'preview_imagen'),
            )
        }),
        ('Opciones de Promoción', {
            'fields': (
                'destacado',
                'en_promocion',
                'descuento',
                'precio_promocion',
            ),
            'classes': ('collapse',)
        }),
    )

    def mostrar_imagen(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />', obj.imagen.url)
        return format_html('<span class="text-muted">Sin imagen</span>')
    
    def preview_imagen(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="200" style="border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" />', obj.imagen.url)
        return format_html('<span class="text-muted">No hay imagen para previsualizar</span>')

    mostrar_imagen.short_description = 'Imagen'
    preview_imagen.short_description = 'Vista previa'

    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('add-product/', self.admin_site.admin_view(self.add_product_view), name='add_product'),
        ]
        return custom_urls + urls

    def add_product_view(self, request):
        if request.method == 'POST':
            try:
                product = Product(
                    nombre=request.POST['nombre'],
                    descripcion=request.POST['descripcion'],
                    precio=request.POST['precio'],
                    destacado=request.POST.get('destacado') == 'on',
                    en_promocion=request.POST.get('en_promocion') == 'on',
                    descuento=request.POST['descuento']
                )
                if 'imagen' in request.FILES:
                    product.imagen = request.FILES['imagen']
                product.save()
                messages.success(request, 'Producto añadido correctamente')
                return redirect('admin:products_product_changelist')
            except Exception as e:
                messages.error(request, f'Error al añadir el producto: {str(e)}')
        
        return render(request, 'admin/products/add_product.html')