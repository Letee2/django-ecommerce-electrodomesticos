from .cart import Cart

class CartCountMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            cart = Cart(request)
            if not 'cart_count' in request.session:
                cart._save_cart_count()
        
        response = self.get_response(request)
        return response