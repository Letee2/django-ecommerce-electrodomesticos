document.addEventListener('DOMContentLoaded', function() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Función para actualizar el contador del carrito
    function updateCartCounter(count) {
        const cartCounters = document.querySelectorAll('.cart-counter');
        cartCounters.forEach(counter => {
            counter.textContent = count;
        });
    }
    
    // Manejador para añadir al carrito
    document.querySelectorAll('.add-to-cart-form').forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            const productId = this.getAttribute('data-product-id');
            
            try {
                const response = await fetch(`/cart/add/${productId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    }
                });
                
                const data = await response.json();
                if (data.success) {
                    updateCartCounter(data.cart_count);
                    
                    const cartModal = new bootstrap.Modal(document.getElementById('cartModal'));
                    cartModal.show();
                    setTimeout(() => {
                        cartModal.hide();
                    }, 1500);
                } else {
                    alert(data.error || 'Error al añadir al carrito');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error al añadir al carrito');
            }
        });
    });
    
    // Manejador para eliminar productos
    document.querySelectorAll('.remove-item').forEach(button => {
        button.addEventListener('click', async function() {
            if (!confirm('¿Estás seguro de que deseas eliminar este producto del carrito?')) {
                return;
            }
            
            const productId = this.getAttribute('data-product-id');
            
            try {
                const response = await fetch(`/cart/remove/${productId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken
                    }
                });
                
                const data = await response.json();
                if (data.success) {
                    updateCartCounter(data.cart_count);
                    window.location.reload();
                } else {
                    alert(data.error || 'Error al eliminar el producto del carrito');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error al eliminar el producto del carrito');
            }
        });
    });
    
    // Manejador para actualizar cantidad
    document.querySelectorAll('.update-quantity').forEach(button => {
        button.addEventListener('click', async function() {
            const productId = this.getAttribute('data-product-id');
            const modal = this.closest('.modal');
            const quantityInput = modal.querySelector('.quantity-input');
            const quantity = parseInt(quantityInput.value);
            
            if (quantity < 1) {
                alert('La cantidad debe ser mayor a 0');
                return;
            }
            
            try {
                const response = await fetch(`/cart/update/${productId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({ quantity: quantity })
                });
                
                const data = await response.json();
                if (data.success) {
                    updateCartCounter(data.cart_count);
                    window.location.reload();
                } else {
                    alert(data.error || 'Error al actualizar el carrito');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error al actualizar el carrito');
            }
        });
    });
});
