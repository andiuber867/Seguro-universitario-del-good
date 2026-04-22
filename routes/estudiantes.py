from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime

estudiantes_bp = Blueprint('estudiantes', __name__, url_prefix='/estudiantes')


@estudiantes_bp.route('/')
@login_required
def lista():
    """Lista de estudiantes con búsqueda"""
    from models import db, Estudiante
    
    buscar = request.args.get('buscar', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    query = Estudiante.query
    
    if buscar:
        query = query.filter(
            db.or_(
                Estudiante.nombre.ilike(f'%{buscar}%'),
                Estudiante.apellido_paterno.ilike(f'%{buscar}%'),
                Estudiante.apellido_materno.ilike(f'%{buscar}%'),
                Estudiante.ci.ilike(f'%{buscar}%'),
                Estudiante.matricula.ilike(f'%{buscar}%'),
                Estudiante.carrera.ilike(f'%{buscar}%')
            )
        )
    
    estudiantes = query.order_by(
        Estudiante.apellido_paterno,
        Estudiante.apellido_materno,
        Estudiante.nombre
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('estudiantes/lista.html',
                         estudiantes=estudiantes,
                         buscar=buscar)


@estudiantes_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    """Registrar nuevo estudiante"""
    from models import db, Estudiante
    
    if request.method == 'POST':
        try:
            ci = request.form.get('ci', '').strip()
            nombre = request.form.get('nombre', '').strip()
            apellido_paterno = request.form.get('apellido_paterno', '').strip()
            apellido_materno = request.form.get('apellido_materno', '').strip()
            fecha_nacimiento_str = request.form.get('fecha_nacimiento')
            sexo = request.form.get('sexo')
            carrera = request.form.get('carrera', '').strip()
            matricula = request.form.get('matricula', '').strip()
            
            # Validaciones
            if not all([ci, nombre, apellido_paterno, fecha_nacimiento_str, sexo, carrera, matricula]):
                flash('Por favor complete todos los campos obligatorios.', 'warning')
                return render_template('estudiantes/nuevo.html')
            
            # Verificar CI duplicado
            if Estudiante.query.filter_by(ci=ci).first():
                flash(f'Ya existe un estudiante registrado con CI {ci}.', 'warning')
                return render_template('estudiantes/nuevo.html')
            
            # Verificar matrícula duplicada
            if Estudiante.query.filter_by(matricula=matricula).first():
                flash(f'Ya existe un estudiante con matrícula {matricula}.', 'warning')
                return render_template('estudiantes/nuevo.html')
            
            # Convertir fecha
            fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, '%Y-%m-%d').date()
            
            # Crear estudiante
            nuevo_estudiante = Estudiante(
                ci=ci,
                nombre=nombre,
                apellido_paterno=apellido_paterno,
                apellido_materno=apellido_materno if apellido_materno else None,
                fecha_nacimiento=fecha_nacimiento,
                sexo=sexo,
                direccion=request.form.get('direccion', '').strip() or None,
                telefono=request.form.get('telefono', '').strip() or None,
                email=request.form.get('email', '').strip() or None,
                carrera=carrera,
                matricula=matricula,
                semestre=request.form.get('semestre', type=int),
                grupo_sanguineo=request.form.get('grupo_sanguineo', '').strip() or None,
                alergias=request.form.get('alergias', '').strip() or None,
                enfermedades_cronicas=request.form.get('enfermedades_cronicas', '').strip() or None,
                cirugias_previas=request.form.get('cirugias_previas', '').strip() or None,
                medicamentos_actuales=request.form.get('medicamentos_actuales', '').strip() or None,
                contacto_emergencia_nombre=request.form.get('contacto_emergencia_nombre', '').strip() or None,
                contacto_emergencia_telefono=request.form.get('contacto_emergencia_telefono', '').strip() or None,
                contacto_emergencia_relacion=request.form.get('contacto_emergencia_relacion', '').strip() or None
            )
            
            db.session.add(nuevo_estudiante)
            db.session.commit()
            
            flash(f'Estudiante {nuevo_estudiante.nombre_completo} registrado exitosamente.', 'success')
            return redirect(url_for('estudiantes.ficha', id=nuevo_estudiante.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar estudiante: {str(e)}', 'danger')
            import traceback
            print(traceback.format_exc())
            return render_template('estudiantes/nuevo.html')
    
    return render_template('estudiantes/nuevo.html')


@estudiantes_bp.route('/<int:id>')
@login_required
def ficha(id):
    """Ver ficha completa del estudiante"""
    from models import db, Estudiante
    
    est = Estudiante.query.get_or_404(id)
    consultas = est.consultas.order_by(db.desc('fecha_hora')).limit(10).all()
    
    return render_template('estudiantes/ficha.html',
                         estudiante=est,
                         consultas=consultas)


@estudiantes_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar datos del estudiante"""
    from models import db, Estudiante
    
    est = Estudiante.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Campos editables ahora incluyen TODO
            ci_nuevo = request.form.get('ci', '').strip()
            matricula_nueva = request.form.get('matricula', '').strip()
            
            # Verificar CI duplicado (si cambió)
            if ci_nuevo != est.ci:
                if Estudiante.query.filter_by(ci=ci_nuevo).first():
                    flash(f'Ya existe un estudiante con CI {ci_nuevo}.', 'warning')
                    return render_template('estudiantes/editar.html', estudiante=est)
                est.ci = ci_nuevo
            
            # Verificar matrícula duplicada (si cambió)
            if matricula_nueva != est.matricula:
                if Estudiante.query.filter_by(matricula=matricula_nueva).first():
                    flash(f'Ya existe un estudiante con matrícula {matricula_nueva}.', 'warning')
                    return render_template('estudiantes/editar.html', estudiante=est)
                est.matricula = matricula_nueva
            
            # Actualizar todos los campos
            est.nombre = request.form.get('nombre', '').strip()
            est.apellido_paterno = request.form.get('apellido_paterno', '').strip()
            est.apellido_materno = request.form.get('apellido_materno', '').strip() or None
            
            # Fecha de nacimiento
            fecha_str = request.form.get('fecha_nacimiento')
            if fecha_str:
                est.fecha_nacimiento = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            
            # Sexo
            est.sexo = request.form.get('sexo')
            
            # Resto de campos
            est.direccion = request.form.get('direccion', '').strip() or None
            est.telefono = request.form.get('telefono', '').strip() or None
            est.email = request.form.get('email', '').strip() or None
            est.carrera = request.form.get('carrera', '').strip()
            est.semestre = request.form.get('semestre', type=int)
            est.grupo_sanguineo = request.form.get('grupo_sanguineo', '').strip() or None
            est.alergias = request.form.get('alergias', '').strip() or None
            est.enfermedades_cronicas = request.form.get('enfermedades_cronicas', '').strip() or None
            est.cirugias_previas = request.form.get('cirugias_previas', '').strip() or None
            est.medicamentos_actuales = request.form.get('medicamentos_actuales', '').strip() or None
            est.contacto_emergencia_nombre = request.form.get('contacto_emergencia_nombre', '').strip() or None
            est.contacto_emergencia_telefono = request.form.get('contacto_emergencia_telefono', '').strip() or None
            est.contacto_emergencia_relacion = request.form.get('contacto_emergencia_relacion', '').strip() or None
            
            db.session.commit()
            flash(f'Datos de {est.nombre_completo} actualizados exitosamente.', 'success')
            return redirect(url_for('estudiantes.ficha', id=est.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar estudiante: {str(e)}', 'danger')
            import traceback
            print(traceback.format_exc())
    
    return render_template('estudiantes/editar.html', estudiante=est)


@estudiantes_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    """Eliminar estudiante"""
    from models import db, Estudiante
    
    est = Estudiante.query.get_or_404(id)
    nombre_completo = est.nombre_completo
    
    try:
        db.session.delete(est)
        db.session.commit()
        flash(f'Estudiante {nombre_completo} eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar estudiante: {str(e)}', 'danger')
    
    return redirect(url_for('estudiantes.lista'))


@estudiantes_bp.route('/buscar-ajax')
@login_required
def buscar_ajax():
    """Búsqueda rápida de estudiantes para autocompletar (AJAX)"""
    from models import db, Estudiante
    
    query = request.args.get('q', '').strip()
    
    if len(query) < 2:
        return jsonify([])
    
    estudiantes = Estudiante.query.filter(
        db.or_(
            Estudiante.nombre.ilike(f'%{query}%'),
            Estudiante.apellido_paterno.ilike(f'%{query}%'),
            Estudiante.ci.ilike(f'%{query}%'),
            Estudiante.matricula.ilike(f'%{query}%')
        )
    ).limit(10).all()
    
    resultados = [{
        'id': e.id,
        'ci': e.ci,
        'nombre': e.nombre_completo,
        'matricula': e.matricula,
        'carrera': e.carrera,
        'edad': e.edad
    } for e in estudiantes]
    
    return jsonify(resultados)