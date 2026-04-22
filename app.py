from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, current_user
from config import config
import os
from datetime import datetime, timezone, timedelta

# Importar modelos
from models import db, Usuario, Estudiante, Consulta, Prescripcion, OrdenReferencia, BOLIVIA_TZ, get_bolivia_time

login_manager = LoginManager()


def create_app(config_name='default'):
    """Factory function para crear la aplicación Flask"""
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión.'
    login_manager.login_message_category = 'info'
    
    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Usuario, int(user_id))
    
    with app.app_context():
        # Crear tablas
        db.create_all()
        
        # Crear usuarios por defecto
        if Usuario.query.count() == 0:
            admin = Usuario(
                username='admin',
                nombre_completo='Administrador Sistema',
                rol='admin',
                email='admin@apsa.uagrm.edu.bo',
                activo=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            medico = Usuario(
                username='dr.perez',
                nombre_completo='Dr. Juan Pérez García',
                rol='medico',
                email='jperez@apsa.uagrm.edu.bo',
                activo=True
            )
            medico.set_password('medico123')
            db.session.add(medico)
            
            enfermera = Usuario(
                username='enf.maria',
                nombre_completo='Lic. María López Sánchez',
                rol='enfermera',
                email='mlopez@apsa.uagrm.edu.bo',
                activo=True
            )
            enfermera.set_password('enfermera123')
            db.session.add(enfermera)
            
            try:
                db.session.commit()
                print("✓ Usuarios creados exitosamente")
            except Exception as e:
                db.session.rollback()
                print(f"Error: {e}")
    
    # Registrar blueprints
    from routes.auth import auth_bp
    from routes.estudiantes import estudiantes_bp
    from routes.consultas import consultas_bp
    from routes.ordenes import ordenes_bp
    from routes.usuarios import usuarios_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(estudiantes_bp)
    app.register_blueprint(consultas_bp)
    app.register_blueprint(ordenes_bp)
    app.register_blueprint(usuarios_bp)
    
    # Rutas principales
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('auth.login'))
    
    @app.route('/dashboard')
    def dashboard():
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        total_estudiantes = Estudiante.query.count()
        
        # Obtener fecha actual en Bolivia
        ahora_bolivia = get_bolivia_time()
        hoy_inicio = ahora_bolivia.replace(hour=0, minute=0, second=0, microsecond=0)
        hoy_fin = ahora_bolivia.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Contar consultas de hoy
        consultas_hoy = Consulta.query.filter(
            Consulta.fecha_hora >= hoy_inicio,
            Consulta.fecha_hora <= hoy_fin
        ).count()
        
        ordenes_pendientes = OrdenReferencia.query.filter_by(estado='pendiente').count()
        ultimas_consultas = Consulta.query.order_by(Consulta.fecha_hora.desc()).limit(5).all()
        
        return render_template('dashboard.html',
                             total_estudiantes=total_estudiantes,
                             consultas_hoy=consultas_hoy,
                             ordenes_pendientes=ordenes_pendientes,
                             ultimas_consultas=ultimas_consultas)
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403
    
    @app.context_processor
    def inject_globals():
        return {
            'app_name': app.config['APP_NAME'],
            'app_version': app.config['APP_VERSION'],
            'hospital_name': app.config['HOSPITAL_NAME'],
            'universidad': app.config['UNIVERSIDAD']
        }
    
    return app


if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV') or 'development')
    app.run(host='0.0.0.0', port=5005, debug=True)