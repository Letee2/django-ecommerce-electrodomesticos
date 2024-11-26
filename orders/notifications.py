from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_order_status_email(order):
    subject = f'Actualización de tu pedido #{order.id}'
    
    context = {
        'order': order,
        'status': order.get_status_display(),
    }
    
    html_message = render_to_string('orders/email/status_update.html', context)
    
    send_mail(
        subject=subject,
        message='',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[order.user.email],
        html_message=html_message
    ) 

def send_order_confirmation_email(order):
    subject = f'Confirmación de pedido #{order.id}'
    
    context = {
        'order': order,
    }
  
    html_message = render_to_string('orders/email/order_confirmation.html', context)
    
    send_mail(
        subject=subject,
        message='',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[order.user.email],
        html_message=html_message
    ) 