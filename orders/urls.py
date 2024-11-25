from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('mis-pedidos/', views.order_list, name='order_list'),
    path('checkout/cod/', views.checkout_cod, name='checkout_cod'),
] 