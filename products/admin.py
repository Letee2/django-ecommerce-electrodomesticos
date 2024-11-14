from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'destacado', 'promocion')
    list_filter = ('destacado', 'promocion')
    search_fields = ('nombre', 'descripcion')