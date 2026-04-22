"""
Módulo de rutas (blueprints) de la aplicación
"""

from routes.auth import auth_bp
from routes.estudiantes import estudiantes_bp
from routes.consultas import consultas_bp
from routes.ordenes import ordenes_bp

__all__ = ['auth_bp', 'estudiantes_bp', 'consultas_bp', 'ordenes_bp']