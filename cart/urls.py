from django.urls import path, include

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('payment/process/', views.process_payment, name='process_payment'),
    path('payment/success/', views.checkout_success, name='payment_success'),
    path('payment/validate/', views.validate_payment, name='validate_payment'),
    path('cart/', include('cart.urls')),
] 