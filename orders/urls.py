from django.urls import path
from . import views

urlpatterns = [
    path('orders/', views.order_list, name='order_list'),
    path('create-order/', views.create_order, name='create_order'),
] 