// Cargar tema guardado al iniciar
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    const savedFontSize = localStorage.getItem('fontSize') || 'normal';
    const animationsEnabled = localStorage.getItem('animations') !== 'false';
    const particlesEnabled = localStorage.getItem('particles') !== 'false';
    
    // Aplicar tema
    setTheme(savedTheme);
    setFontSize(savedFontSize);
    
    // Configurar switches
    const animToggle = document.getElementById('animationsToggle');
    const particlesToggle = document.getElementById('particlesToggle');
    
    if (animToggle) {
        animToggle.checked = animationsEnabled;
        
        if (!animationsEnabled) {
            document.body.classList.add('no-animations');
        }
        
        animToggle.addEventListener('change', function(e) {
            if (e.target.checked) {
                document.body.classList.remove('no-animations');
                localStorage.setItem('animations', 'true');
                console.log('Animaciones activadas');
            } else {
                document.body.classList.add('no-animations');
                localStorage.setItem('animations', 'false');
                console.log('Animaciones desactivadas');
            }
        });
    }
    
    if (particlesToggle) {
        particlesToggle.checked = particlesEnabled;
        
        const particles = document.querySelector('.background-particles');
        if (particles) {
            particles.style.display = particlesEnabled ? 'block' : 'none';
        }
        
        particlesToggle.addEventListener('change', function(e) {
            const particles = document.querySelector('.background-particles');
            if (particles) {
                if (e.target.checked) {
                    particles.style.display = 'block';
                    localStorage.setItem('particles', 'true');
                    console.log('Partículas activadas');
                } else {
                    particles.style.display = 'none';
                    localStorage.setItem('particles', 'false');
                    console.log('Partículas desactivadas');
                }
            }
        });
    }
    
    // Marcar tema activo
    updateActiveTheme(savedTheme);
});

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    updateActiveTheme(theme);
    
    // Animación de cambio
    document.body.style.transition = 'all 0.5s ease';
    
    console.log('Tema cambiado a:', theme);
}

function updateActiveTheme(theme) {
    // Remover clase active de todas las tarjetas de tema
    document.querySelectorAll('.theme-card').forEach(card => {
        card.classList.remove('active');
    });
    
    // Agregar clase active a la tarjeta del tema actual
    const themeCards = {
        'light': 0,
        'dark': 1,
        'pink': 2,
        'green': 3,
        'uagrm': 4
    };
    
    const cards = document.querySelectorAll('.theme-card');
    if (cards[themeCards[theme]]) {
        cards[themeCards[theme]].classList.add('active');
    }
}

function setFontSize(size) {
    document.documentElement.setAttribute('data-font-size', size);
    localStorage.setItem('fontSize', size);
    
    // Actualizar botones activos
    document.querySelectorAll('.btn-group .btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    const btnMap = {
        'small': 0,
        'normal': 1,
        'large': 2
    };
    
    const buttons = document.querySelectorAll('.btn-group .btn');
    if (buttons[btnMap[size]]) {
        buttons[btnMap[size]].classList.add('active');
    }
    
    console.log('Tamaño de fuente cambiado a:', size);
}

// Efectos de hover en cards (eliminados a petición del usuario)
document.addEventListener('DOMContentLoaded', function() {
    // No se agregan efectos de movimiento en hover
});

// Efecto de ripple en botones
document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (document.body.classList.contains('no-animations')) return;
            
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
});

// Manejar clicks en dropdown items que abren modales
document.addEventListener('DOMContentLoaded', function() {
    const modalTriggers = document.querySelectorAll('[data-bs-toggle="modal"]');
    
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const targetModal = this.getAttribute('data-bs-target');
            const modalElement = document.querySelector(targetModal);
            
            if (modalElement) {
                const modal = new bootstrap.Modal(modalElement);
                modal.show();
                
                // Cerrar el dropdown después de abrir el modal
                const dropdown = bootstrap.Dropdown.getInstance(document.getElementById('navbarDropdown'));
                if (dropdown) {
                    dropdown.hide();
                }
            }
        });
    });
});

// ⭐ FIX: Limpiar modal backdrop cuando se cierra
document.addEventListener('DOMContentLoaded', function() {
    const modals = document.querySelectorAll('.modal');
    
    modals.forEach(modal => {
        modal.addEventListener('hidden.bs.modal', function() {
            // Remover todos los backdrops que puedan quedar
            const backdrops = document.querySelectorAll('.modal-backdrop');
            backdrops.forEach(backdrop => backdrop.remove());
            
            // Asegurar que body pueda hacer scroll
            document.body.classList.remove('modal-open');
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
            
            console.log('Modal cerrado y limpiado');
        });
    });
});

// Animación de entrada para elementos
const observeElements = () => {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1
    });
    
    document.querySelectorAll('.card, .table').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'all 0.5s ease';
        observer.observe(el);
    });
};

// Llamar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', observeElements);
} else {
    observeElements();
}

console.log('Sistema de temas cargado correctamente');