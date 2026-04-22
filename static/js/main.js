/**
 * APSA - Sistema de Gestión de Salud Estudiantil
 * JavaScript Principal
 */

// ========================================
// DOCUMENT READY
// ========================================

$(document).ready(function() {
    console.log('APSA System - Ready');
    
    // Inicializar tooltips de Bootstrap
    initializeTooltips();
    
    // Auto-dismiss alerts después de 5 segundos
    autoDismissAlerts();
    
    // Confirmaciones para acciones peligrosas
    setupDeleteConfirmations();
    
    // Búsqueda con debounce
    setupSearchDebounce();
    
    // Animaciones al hacer scroll
    setupScrollAnimations();
    
    // Validación de formularios
    setupFormValidations();
});

// ========================================
// TOOLTIPS
// ========================================

function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// ========================================
// AUTO DISMISS ALERTS
// ========================================

function autoDismissAlerts() {
    $('.alert:not(.alert-permanent)').each(function() {
        const alert = $(this);
        setTimeout(function() {
            alert.fadeOut(500, function() {
                $(this).remove();
            });
        }, 5000);
    });
}

// ========================================
// DELETE CONFIRMATIONS
// ========================================

function setupDeleteConfirmations() {
    $('[data-confirm]').on('click', function(e) {
        const message = $(this).data('confirm') || '¿Está seguro de realizar esta acción?';
        if (!confirm(message)) {
            e.preventDefault();
            return false;
        }
    });
}

// ========================================
// SEARCH WITH DEBOUNCE
// ========================================

function setupSearchDebounce() {
    let searchTimeout;
    
    $('input[data-search-debounce]').on('input', function() {
        const input = $(this);
        const form = input.closest('form');
        
        clearTimeout(searchTimeout);
        
        searchTimeout = setTimeout(function() {
            form.submit();
        }, 500);
    });
}

// ========================================
// SCROLL ANIMATIONS
// ========================================

function setupScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, {
        threshold: 0.1
    });
    
    document.querySelectorAll('.card').forEach(card => {
        observer.observe(card);
    });
}

// ========================================
// FORM VALIDATIONS
// ========================================

function setupFormValidations() {
    // Validación de CI (solo números)
    $('input[name="ci"]').on('input', function() {
        this.value = this.value.replace(/[^0-9]/g, '');
    });
    
    // Validación de teléfono (solo números)
    $('input[type="tel"]').on('input', function() {
        this.value = this.value.replace(/[^0-9]/g, '');
    });
    
    // Validación de matrícula
    $('input[name="matricula"]').on('input', function() {
        this.value = this.value.replace(/[^0-9A-Za-z]/g, '');
    });
}

// ========================================
// LOADING SPINNER
// ========================================

function showLoadingSpinner() {
    const spinner = `
        <div class="spinner-overlay" id="loadingSpinner">
            <div class="spinner-border spinner-border-custom text-light" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
        </div>
    `;
    $('body').append(spinner);
}

function hideLoadingSpinner() {
    $('#loadingSpinner').fadeOut(300, function() {
        $(this).remove();
    });
}

// ========================================
// BÚSQUEDA DE ESTUDIANTES (AUTOCOMPLETE)
// ========================================

function setupEstudianteSearch(inputId, resultsId) {
    const input = $('#' + inputId);
    const results = $('#' + resultsId);
    let searchTimeout;
    
    input.on('input', function() {
        const query = $(this).val().trim();
        
        clearTimeout(searchTimeout);
        
        if (query.length < 2) {
            results.hide();
            return;
        }
        
        searchTimeout = setTimeout(function() {
            $.ajax({
                url: '/estudiantes/buscar-ajax',
                method: 'GET',
                data: { q: query },
                success: function(data) {
                    displaySearchResults(data, results);
                },
                error: function() {
                    console.error('Error en búsqueda');
                }
            });
        }, 300);
    });
    
    // Cerrar resultados al hacer clic fuera
    $(document).on('click', function(e) {
        if (!$(e.target).closest('#' + inputId).length) {
            results.hide();
        }
    });
}

function displaySearchResults(estudiantes, resultsContainer) {
    if (estudiantes.length === 0) {
        resultsContainer.html('<div class="list-group-item">No se encontraron resultados</div>');
        resultsContainer.show();
        return;
    }
    
    let html = '';
    estudiantes.forEach(function(est) {
        html += `
            <a href="/estudiantes/${est.id}" class="list-group-item list-group-item-action">
                <div class="d-flex w-100 justify-content-between">
                    <h6 class="mb-1">${est.nombre}</h6>
                    <small>${est.edad} años</small>
                </div>
                <p class="mb-1"><small>CI: ${est.ci} | Mat: ${est.matricula}</small></p>
                <small>${est.carrera}</small>
            </a>
        `;
    });
    
    resultsContainer.html(html);
    resultsContainer.show();
}

// ========================================
// CALCULAR IMC
// ========================================

function calcularIMC(peso, talla) {
    if (!peso || !talla || peso <= 0 || talla <= 0) {
        return null;
    }
    
    const tallaMts = talla / 100;
    const imc = peso / (tallaMts * tallaMts);
    
    return {
        valor: imc.toFixed(2),
        clasificacion: getClasificacionIMC(imc)
    };
}

function getClasificacionIMC(imc) {
    if (imc < 18.5) return 'Bajo peso';
    if (imc < 25) return 'Normal';
    if (imc < 30) return 'Sobrepeso';
    return 'Obesidad';
}

// ========================================
// PRINT FUNCTIONALITY
// ========================================

function printElement(elementId) {
    const content = document.getElementById(elementId);
    const printWindow = window.open('', '', 'height=600,width=800');
    
    printWindow.document.write('<html><head><title>Imprimir</title>');
    printWindow.document.write('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">');
    printWindow.document.write('</head><body>');
    printWindow.document.write(content.innerHTML);
    printWindow.document.write('</body></html>');
    
    printWindow.document.close();
    printWindow.focus();
    
    setTimeout(function() {
        printWindow.print();
        printWindow.close();
    }, 250);
}

// ========================================
// COPIAR AL PORTAPAPELES
// ========================================

function copiarAlPortapapeles(texto) {
    navigator.clipboard.writeText(texto).then(function() {
        alert('Copiado al portapapeles');
    }).catch(function(err) {
        console.error('Error al copiar: ', err);
    });
}

// ========================================
// FORMATEAR FECHA
// ========================================

function formatearFecha(fecha) {
    const meses = [
        'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
        'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
    ];
    
    const d = new Date(fecha);
    return `${d.getDate()} de ${meses[d.getMonth()]} de ${d.getFullYear()}`;
}

// ========================================
// VALIDAR EDAD MÍNIMA
// ========================================

function validarEdadMinima(fechaNacimiento, edadMinima = 18) {
    const hoy = new Date();
    const nacimiento = new Date(fechaNacimiento);
    let edad = hoy.getFullYear() - nacimiento.getFullYear();
    const mes = hoy.getMonth() - nacimiento.getMonth();
    
    if (mes < 0 || (mes === 0 && hoy.getDate() < nacimiento.getDate())) {
        edad--;
    }
    
    return edad >= edadMinima;
}

// ========================================
// EXPORTAR FUNCIONES GLOBALES
// ========================================

window.apsaUtils = {
    showLoading: showLoadingSpinner,
    hideLoading: hideLoadingSpinner,
    calcularIMC: calcularIMC,
    printElement: printElement,
    copiarAlPortapapeles: copiarAlPortapapeles,
    formatearFecha: formatearFecha,
    validarEdadMinima: validarEdadMinima
};

// ========================================
// CONSOLE MESSAGE
// ========================================

console.log('%c APSA - Sistema de Gestión de Salud Estudiantil ', 
    'background: #0d6efd; color: white; font-size: 16px; padding: 10px;');
console.log('%c UAGRM Yapacaní - 2024 ', 
    'background: #198754; color: white; font-size: 12px; padding: 5px;');