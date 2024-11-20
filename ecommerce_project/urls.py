"""
URL configuration for ecommerce_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from products.views import home, product_detail, catalog
from users import views as user_views
from cart import views as cart_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('registro/', user_views.registro, name='registro'),
    path('login/', user_views.iniciar_sesion, name='login'),
    path('logout/', user_views.cerrar_sesion, name='logout'),
    path('cart/', cart_views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', cart_views.add_to_cart, name='add_to_cart'),
    path('checkout/cod/', cart_views.checkout_cod, name='checkout_cod'),
    path('create-checkout-session/', cart_views.create_checkout_session, name='create_checkout_session'),
    path('checkout/success/', cart_views.checkout_success, name='checkout_success'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('profile/', user_views.profile, name='profile'),
    path('catalogo/', catalog, name='catalog'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
