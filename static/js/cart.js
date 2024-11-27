document.addEventListener('DOMContentLoaded', function() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Inicializar los toasts
    const errorToast = new bootstrap.Toast(document.getElementById('errorToast'), {
        delay: 3000,
        autohide: true
    });
    
    const warningToast = new bootstrap.Toast(document.getElementById('warningToast'), {
        delay: 3000,
        autohide: true
    });
    
    const successToast = new bootstrap.Toast(document.getElementById('successToast'), {
        delay: 1500,
        autohide: true
    });
    
    function showError(message) {
        document.getElementById('errorToastText').textContent = message;
        errorToast.show();
    }
    
    function showWarning(message) {
        document.getElementById('warningToastText').textContent = message;
        warningToast.show();
    }
    
    function showSuccess(message) {
        document.getElementById('successToastText').textContent = message;
        successToast.show();
    }
    
    // Función para actualizar el contador del carrito
    function updateCartCounter(count) {
        const cartCounters = document.querySelectorAll('#cart-counter');
        cartCounters.forEach(counter => {
            counter.textContent = count;
        });
    }
    
    // Actualizar el contador al cargar la página
    const currentCount = document.querySelector('#cart-counter')?.textContent || '0';
    updateCartCounter(currentCount);
    
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
                    showError(data.error || 'Error al añadir al carrito');
                }
            } catch (error) {
                console.error('Error:', error);
                showError('Error al añadir al carrito');
            }
        });
    });
    
    // Manejador para eliminar productos
    document.querySelectorAll('.remove-item').forEach(button => {
        button.addEventListener('click', async function() {
            const productId = this.getAttribute('data-product-id');
            const modal = bootstrap.Modal.getInstance(this.closest('.modal'));
            
            // Mostrar toast de confirmación
            const confirmDeleteToast = new bootstrap.Toast(document.getElementById('confirmDeleteToast'), {
                autohide: false
            });
            
            // Configurar botones de confirmación
            const confirmButton = document.getElementById('confirmDeleteButton');
            const cancelButton = document.getElementById('cancelDeleteButton');
            
            const handleDelete = async () => {
                confirmDeleteToast.hide();
                try {
                    const response = await fetch(`/cart/remove/${productId}/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        }
                    });
                    
                    const data = await response.json();
                    if (data.success) {
                        showWarning('Producto eliminado del carrito');
                        setTimeout(() => {
                            modal.hide();
                            updateCartCounter(data.cart_count);
                            window.location.reload();
                        }, 1500);
                    } else {
                        showError(data.error || 'Error al eliminar el producto');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    showError('Error al eliminar el producto');
                }
            };
            
            confirmButton.onclick = handleDelete;
            cancelButton.onclick = () => confirmDeleteToast.hide();
            
            confirmDeleteToast.show();
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
                showWarning('La cantidad debe ser mayor a 0');
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
                    showSuccess('Cantidad actualizada correctamente');
                    setTimeout(() => {
                        bootstrap.Modal.getInstance(modal).hide();
                        updateCartCounter(data.cart_count);
                        window.location.reload();
                    }, 1500);
                } else {
                    showError(data.error || 'Error al actualizar la cantidad');
                }
            } catch (error) {
                console.error('Error:', error);
                showError('Error al actualizar la cantidad');
            }
        });
    });
});
