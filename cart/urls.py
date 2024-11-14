from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.cart_detail, name='cart_detail'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('payment/success/', views.payment_success, name='payment_success'),
] 