document.addEventListener('DOMContentLoaded', function() {
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');
    const cartCounter = document.getElementById('cart-counter');
    
    addToCartForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const productId = this.getAttribute('data-product-id');
            const csrfToken = this.querySelector('[name=csrfmiddlewaretoken]').value;
            
            fetch(`/cart/add/${productId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Actualizar contador del carrito
                    if (cartCounter) {
                        cartCounter.textContent = data.cart_count;
                        cartCounter.classList.add('pulse-animation');
                        setTimeout(() => {
                            cartCounter.classList.remove('pulse-animation');
                        }, 500);
                    }
                    
                    // Mostrar mensaje de éxito
                    const toast = document.createElement('div');
                    toast.className = 'toast-notification success';
                    toast.innerHTML = `
                        <i class="fas fa-check-circle me-2"></i>
                        Producto añadido al carrito
                    `;
                    document.body.appendChild(toast);
                    
                    setTimeout(() => {
                        toast.remove();
                    }, 2000);
                }
            });
        });
    });

    // Manejador para botones de eliminar
    document.querySelectorAll('.remove-from-cart').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.getAttribute('data-product-id');
            const productName = this.getAttribute('data-product-name');
            const currentQuantity = parseInt(this.closest('.cart-item').querySelector('.quantity-display').textContent.split(': ')[1]);
            
            Swal.fire({
                title: 'Editar producto',
                html: `
                    <p>¿Qué deseas hacer con <strong>${productName}</strong>?</p>
                    <div class="mb-3">
                        <label class="form-label">Modificar cantidad:</label>
                        <input type="number" id="swal-quantity" 
                               class="form-control text-center mx-auto" 
                               style="max-width: 150px"
                               value="${currentQuantity}"
                               min="1"
                               max="${this.getAttribute('data-stock')}">
                    </div>
                `,
                icon: 'info',
                showCancelButton: true,
                showDenyButton: true,
                confirmButtonColor: '#0d6efd',
                denyButtonColor: '#dc3545',
                cancelButtonColor: '#6c757d',
                confirmButtonText: 'Actualizar cantidad',
                denyButtonText: 'Eliminar del carrito',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    const newQuantity = document.getElementById('swal-quantity').value;
                    updateCartQuantity(productId, newQuantity);
                } else if (result.isDenied) {
                    removeFromCart(productId);
                }
            });
        });
    });
});

function removeFromCart(productId) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch(`/cart/remove/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const itemRow = document.querySelector(`[data-product-id="${productId}"]`).closest('.cart-item');
            itemRow.style.transition = 'all 0.3s ease';
            itemRow.style.opacity = '0';
            itemRow.style.transform = 'translateX(20px)';
            
            setTimeout(() => {
                itemRow.remove();
                if (cartCounter) cartCounter.textContent = data.cart_count;
                
                const cartTotal = document.querySelector('.cart-total');
                if (cartTotal) cartTotal.textContent = `€${data.total.toFixed(2)}`;
                
                if (data.cart_count === 0) location.reload();
            }, 300);
        }
    });
}

function updateCartQuantity(productId, newQuantity) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch(`/cart/update/${productId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ quantity: parseInt(newQuantity) })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const itemRow = document.querySelector(`[data-product-id="${productId}"]`).closest('.cart-item');
            const quantityDisplay = itemRow.querySelector('.quantity-display');
            const itemTotal = itemRow.querySelector('.item-total');
            
            quantityDisplay.textContent = `Cantidad: ${data.quantity}`;
            itemTotal.textContent = `€${data.item_total.toFixed(2)}`;
            
            if (cartCounter) cartCounter.textContent = data.cart_count;
            
            const cartTotal = document.querySelector('.cart-total');
            if (cartTotal) cartTotal.textContent = `€${data.total.toFixed(2)}`;
            
            Swal.fire({
                title: 'Cantidad actualizada',
                icon: 'success',
                timer: 1500,
                showConfirmButton: false
            });
        }
    });
}
