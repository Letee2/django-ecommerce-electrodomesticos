document.addEventListener('DOMContentLoaded', function() {
    // Selecciona todos los mensajes
    const messages = document.querySelectorAll('.alert');
    
    // Para cada mensaje
    messages.forEach(function(message) {
        // Añade clase de animación
        message.classList.add('fade-in');
        
        // Programa la eliminación después de 2 segundos
        setTimeout(function() {
            message.classList.add('fade-out');
            setTimeout(function() {
                message.remove();
            }, 300); // 300ms para la animación de desvanecimiento
        }, 2000);
    });
});
