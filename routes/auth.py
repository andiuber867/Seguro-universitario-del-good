from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from urllib.parse import urlparse

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión"""
    # Importar DENTRO de la función
    from models import db, Usuario
    
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)
        
        if not username or not password:
            flash('Por favor ingrese usuario y contraseña.', 'warning')
            return render_template('login.html')
        
        user = Usuario.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            flash('Usuario o contraseña incorrectos.', 'danger')
            return render_template('login.html')
        
        if not user.activo:
            flash('Su cuenta está desactivada. Contacte al administrador.', 'warning')
            return render_template('login.html')
        
        login_user(user, remember=remember)
        user.update_last_access()
        
        flash(f'¡Bienvenido/a {user.nombre_completo}!', 'success')
        
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('dashboard')
        
        return redirect(next_page)
    
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """Cerrar sesión"""
    if current_user.is_authenticated:
        nombre = current_user.nombre_completo
        logout_user()
        flash(f'Sesión cerrada. ¡Hasta pronto {nombre}!', 'info')
    
    return redirect(url_for('auth.login'))


@auth_bp.route('/perfil')
def perfil():
    """Ver perfil del usuario actual"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    return render_template('auth/perfil.html')


@auth_bp.route('/cambiar-password', methods=['GET', 'POST'])
def cambiar_password():
    """Cambiar contraseña del usuario actual"""
    from models import db
    
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        password_actual = request.form.get('password_actual', '')
        password_nueva = request.form.get('password_nueva', '')
        password_confirmar = request.form.get('password_confirmar', '')
        
        if not current_user.check_password(password_actual):
            flash('La contraseña actual es incorrecta.', 'danger')
            return render_template('auth/cambiar_password.html')
        
        if len(password_nueva) < 6:
            flash('La nueva contraseña debe tener al menos 6 caracteres.', 'warning')
            return render_template('auth/cambiar_password.html')
        
        if password_nueva != password_confirmar:
            flash('Las contraseñas nuevas no coinciden.', 'warning')
            return render_template('auth/cambiar_password.html')
        
        current_user.set_password(password_nueva)
        db.session.commit()
        
        flash('Contraseña cambiada exitosamente.', 'success')
        return redirect(url_for('auth.perfil'))
    
    return render_template('auth/cambiar_password.html')