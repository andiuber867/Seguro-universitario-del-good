from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')


def admin_required(f):
    """Decorador para requerir permisos de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('No tienes permisos para acceder a esta sección.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@usuarios_bp.route('/')
@login_required
@admin_required
def lista():
    """Lista de usuarios del sistema"""
    from models import Usuario
    
    usuarios = Usuario.query.order_by(Usuario.nombre_completo).all()
    return render_template('usuarios/lista.html', usuarios=usuarios)


@usuarios_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo():
    """Crear nuevo usuario"""
    from models import db, Usuario
    
    if request.method == 'POST':
        try:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            password_confirm = request.form.get('password_confirm', '').strip()
            nombre_completo = request.form.get('nombre_completo', '').strip()
            rol = request.form.get('rol', '').strip()
            email = request.form.get('email', '').strip()
            telefono = request.form.get('telefono', '').strip()
            
            # Validaciones
            if not all([username, password, nombre_completo, rol, email]):
                flash('Por favor complete todos los campos obligatorios.', 'warning')
                return render_template('usuarios/nuevo.html')
            
            if password != password_confirm:
                flash('Las contraseñas no coinciden.', 'warning')
                return render_template('usuarios/nuevo.html')
            
            if len(password) < 6:
                flash('La contraseña debe tener al menos 6 caracteres.', 'warning')
                return render_template('usuarios/nuevo.html')
            
            # Verificar si el username ya existe
            if Usuario.query.filter_by(username=username).first():
                flash(f'El nombre de usuario "{username}" ya está en uso.', 'warning')
                return render_template('usuarios/nuevo.html')
            
            # Verificar si el email ya existe
            if Usuario.query.filter_by(email=email).first():
                flash(f'El email "{email}" ya está registrado.', 'warning')
                return render_template('usuarios/nuevo.html')
            
            # Crear nuevo usuario
            nuevo_usuario = Usuario(
                username=username,
                nombre_completo=nombre_completo,
                rol=rol,
                email=email,
                telefono=telefono if telefono else None,
                activo=True
            )
            nuevo_usuario.set_password(password)
            
            db.session.add(nuevo_usuario)
            db.session.commit()
            
            flash(f'Usuario {nuevo_usuario.nombre_completo} creado exitosamente.', 'success')
            return redirect(url_for('usuarios.lista'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear usuario: {str(e)}', 'danger')
    
    return render_template('usuarios/nuevo.html')


@usuarios_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar(id):
    """Editar usuario existente"""
    from models import db, Usuario
    
    usuario = Usuario.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            usuario.nombre_completo = request.form.get('nombre_completo', '').strip()
            usuario.rol = request.form.get('rol', '').strip()
            usuario.email = request.form.get('email', '').strip()
            usuario.telefono = request.form.get('telefono', '').strip() or None
            usuario.activo = request.form.get('activo') == 'on'
            
            # Si se proporciona nueva contraseña
            password = request.form.get('password', '').strip()
            if password:
                if len(password) < 6:
                    flash('La contraseña debe tener al menos 6 caracteres.', 'warning')
                    return render_template('usuarios/editar.html', usuario=usuario)
                usuario.set_password(password)
            
            db.session.commit()
            flash(f'Usuario {usuario.nombre_completo} actualizado exitosamente.', 'success')
            return redirect(url_for('usuarios.lista'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar usuario: {str(e)}', 'danger')
    
    return render_template('usuarios/editar.html', usuario=usuario)


@usuarios_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar(id):
    """Eliminar usuario"""
    from models import db, Usuario
    
    usuario = Usuario.query.get_or_404(id)
    
    # No permitir eliminar el propio usuario
    if usuario.id == current_user.id:
        flash('No puedes eliminar tu propio usuario.', 'warning')
        return redirect(url_for('usuarios.lista'))
    
    try:
        nombre = usuario.nombre_completo
        db.session.delete(usuario)
        db.session.commit()
        flash(f'Usuario {nombre} eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar usuario: {str(e)}', 'danger')
    
    return redirect(url_for('usuarios.lista'))