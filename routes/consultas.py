from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime

consultas_bp = Blueprint('consultas', __name__, url_prefix='/consultas')


@consultas_bp.route('/')
@login_required
def lista():
    """Lista de consultas con filtros por estado"""
    from models import db, Consulta
    
    page = request.args.get('page', 1, type=int)
    estado = request.args.get('estado', 'todas')
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    per_page = 20
    
    query = Consulta.query
    
    # Filtrar por estado
    if estado != 'todas':
        query = query.filter_by(estado=estado)
    
    if fecha_desde:
        fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d')
        query = query.filter(Consulta.fecha_hora >= fecha_desde_dt)
    
    if fecha_hasta:
        fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d')
        fecha_hasta_dt = fecha_hasta_dt.replace(hour=23, minute=59, second=59)
        query = query.filter(Consulta.fecha_hora <= fecha_hasta_dt)
    
    consultas = query.order_by(
        Consulta.fecha_hora.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('consultas/lista.html',
                         consultas=consultas,
                         estado_actual=estado,
                         fecha_desde=fecha_desde,
                         fecha_hasta=fecha_hasta)


@consultas_bp.route('/pendientes')
@login_required
def pendientes():
    """Ver solo consultas pendientes (para médicos)"""
    from models import Consulta
    
    if not current_user.can_complete_consulta():
        flash('No tienes permisos para acceder a esta sección.', 'danger')
        return redirect(url_for('consultas.lista'))
    
    consultas = Consulta.query.filter_by(estado='pendiente').order_by(Consulta.fecha_hora.desc()).all()
    
    return render_template('consultas/pendientes.html', consultas=consultas)


@consultas_bp.route('/nueva/<int:estudiante_id>', methods=['GET', 'POST'])
@login_required
def nueva(estudiante_id):
    """Registrar nueva consulta"""
    from models import db, Estudiante, Consulta, Prescripcion
    
    # Verificar permisos
    if not current_user.can_register_consulta():
        flash('No tienes permisos para registrar consultas.', 'danger')
        return redirect(url_for('dashboard'))
    
    est = Estudiante.query.get_or_404(estudiante_id)
    
    if request.method == 'POST':
        try:
            # Datos básicos que todos pueden ingresar
            nueva_consulta = Consulta(
                estudiante_id=est.id,
                usuario_id=current_user.id,
                motivo_consulta=request.form.get('motivo_consulta', '').strip(),
                presion_arterial=request.form.get('presion_arterial', '').strip() or None,
                frecuencia_cardiaca=request.form.get('frecuencia_cardiaca', type=int),
                temperatura=request.form.get('temperatura', type=float),
                frecuencia_respiratoria=request.form.get('frecuencia_respiratoria', type=int),
                saturacion_oxigeno=request.form.get('saturacion_oxigeno', type=int),
                peso=request.form.get('peso', type=float),
                talla=request.form.get('talla', type=float),
                examen_fisico=request.form.get('examen_fisico', '').strip() or None,
                estado='pendiente'  # Siempre inicia en pendiente
            )
            
            # Solo médicos/admins pueden agregar estos campos
            if current_user.can_complete_consulta():
                nueva_consulta.diagnostico = request.form.get('diagnostico', '').strip() or None
                nueva_consulta.plan_tratamiento = request.form.get('plan_tratamiento', '').strip() or None
                nueva_consulta.indicaciones = request.form.get('indicaciones', '').strip() or None
                nueva_consulta.observaciones = request.form.get('observaciones', '').strip() or None
            
            if not nueva_consulta.motivo_consulta:
                flash('El motivo de consulta es obligatorio.', 'warning')
                return render_template('consultas/nueva.html', estudiante=est)
            
            db.session.add(nueva_consulta)
            db.session.flush()
            
            # Solo médicos/admins pueden prescribir medicamentos
            if current_user.can_complete_consulta():
                medicamentos = request.form.getlist('medicamento[]')
                dosis_list = request.form.getlist('dosis[]')
                frecuencias = request.form.getlist('frecuencia[]')
                duraciones = request.form.getlist('duracion[]')
                
                tiene_medicamentos = False
                for i, medicamento in enumerate(medicamentos):
                    if medicamento.strip():
                        tiene_medicamentos = True
                        prescripcion = Prescripcion(
                            consulta_id=nueva_consulta.id,
                            medicamento=medicamento.strip(),
                            dosis=dosis_list[i].strip() if i < len(dosis_list) else '',
                            frecuencia=frecuencias[i].strip() if i < len(frecuencias) else '',
                            duracion_dias=int(duraciones[i]) if i < len(duraciones) and duraciones[i] else None,
                            via_administracion='Oral'
                        )
                        db.session.add(prescripcion)
                
                # Si hay medicamentos, la consulta se completa
                if tiene_medicamentos:
                    nueva_consulta.estado = 'completada'
            
            db.session.commit()
            
            mensaje = f'Consulta registrada exitosamente para {est.nombre_completo}.'
            if nueva_consulta.estado == 'pendiente':
                mensaje += ' La consulta está pendiente de atención médica.'
            
            flash(mensaje, 'success')
            
            # Solo médicos pueden generar órdenes
            if current_user.can_create_orden() and request.form.get('requiere_referencia') == 'si':
                return redirect(url_for('ordenes.nueva', consulta_id=nueva_consulta.id))
            
            return redirect(url_for('estudiantes.ficha', id=est.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar consulta: {str(e)}', 'danger')
            import traceback
            print(traceback.format_exc())
    
    return render_template('consultas/nueva.html', estudiante=est)


@consultas_bp.route('/<int:id>')
@login_required
def ver(id):
    """Ver detalle de consulta"""
    from models import Consulta
    
    cons = Consulta.query.get_or_404(id)
    prescripciones = cons.prescripciones.all()
    
    return render_template('consultas/ver.html',
                         consulta=cons,
                         prescripciones=prescripciones)


@consultas_bp.route('/<int:id>/atender', methods=['GET', 'POST'])
@login_required
def atender(id):
    """Atender consulta pendiente - SOLO MÉDICOS"""
    from models import db, Consulta, Prescripcion
    
    if not current_user.can_complete_consulta():
        flash('No tienes permisos para atender consultas.', 'danger')
        return redirect(url_for('consultas.lista'))
    
    consulta = Consulta.query.get_or_404(id)
    
    if consulta.estado == 'completada':
        flash('Esta consulta ya fue completada.', 'info')
        return redirect(url_for('consultas.ver', id=id))
    
    if request.method == 'POST':
        try:
            # Actualizar datos médicos
            consulta.diagnostico = request.form.get('diagnostico', '').strip() or None
            consulta.plan_tratamiento = request.form.get('plan_tratamiento', '').strip() or None
            consulta.indicaciones = request.form.get('indicaciones', '').strip() or None
            consulta.observaciones = request.form.get('observaciones', '').strip() or None
            
            accion = request.form.get('accion')
            
            if accion == 'generar_orden':
                # Cambiar a estado "en_referencia" y crear orden
                consulta.estado = 'en_referencia'
                db.session.commit()
                flash('Consulta actualizada. Genera la orden de referencia.', 'success')
                return redirect(url_for('ordenes.nueva', consulta_id=consulta.id))
            
            elif accion == 'medicar':
                # Registrar prescripciones y completar consulta
                medicamentos = request.form.getlist('medicamento[]')
                dosis_list = request.form.getlist('dosis[]')
                frecuencias = request.form.getlist('frecuencia[]')
                duraciones = request.form.getlist('duracion[]')
                
                tiene_medicamentos = False
                for i, medicamento in enumerate(medicamentos):
                    if medicamento.strip():
                        tiene_medicamentos = True
                        prescripcion = Prescripcion(
                            consulta_id=consulta.id,
                            medicamento=medicamento.strip(),
                            dosis=dosis_list[i].strip() if i < len(dosis_list) else '',
                            frecuencia=frecuencias[i].strip() if i < len(frecuencias) else '',
                            duracion_dias=int(duraciones[i]) if i < len(duraciones) and duraciones[i] else None,
                            via_administracion='Oral'
                        )
                        db.session.add(prescripcion)
                
                if tiene_medicamentos:
                    consulta.estado = 'completada'
                    db.session.commit()
                    flash('Consulta completada con prescripciones.', 'success')
                    return redirect(url_for('consultas.ver', id=consulta.id))
                else:
                    flash('Debes agregar al menos un medicamento para completar la consulta.', 'warning')
                    return render_template('consultas/atender.html', consulta=consulta)
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al atender consulta: {str(e)}', 'danger')
    
    return render_template('consultas/atender.html', consulta=consulta)


@consultas_bp.route('/<int:id>/completar-referencia', methods=['POST'])
@login_required
def completar_referencia(id):
    """Completar consulta después de orden completada - SOLO MÉDICOS"""
    from models import db, Consulta, Prescripcion
    
    if not current_user.can_complete_consulta():
        flash('No tienes permisos para completar consultas.', 'danger')
        return redirect(url_for('consultas.lista'))
    
    consulta = Consulta.query.get_or_404(id)
    
    if consulta.estado != 'en_referencia':
        flash('Esta consulta no está en estado de referencia.', 'warning')
        return redirect(url_for('consultas.ver', id=id))
    
    # Verificar que la orden esté completada
    if not consulta.orden_referencia or consulta.orden_referencia.estado != 'completada':
        flash('La orden de referencia debe estar completada primero.', 'warning')
        return redirect(url_for('consultas.ver', id=id))
    
    try:
        # Actualizar diagnóstico final
        consulta.diagnostico = request.form.get('diagnostico_final', '').strip()
        consulta.plan_tratamiento = request.form.get('plan_tratamiento_final', '').strip()
        consulta.indicaciones = request.form.get('indicaciones_final', '').strip()
        
        # Registrar prescripciones
        medicamentos = request.form.getlist('medicamento[]')
        dosis_list = request.form.getlist('dosis[]')
        frecuencias = request.form.getlist('frecuencia[]')
        duraciones = request.form.getlist('duracion[]')
        
        tiene_medicamentos = False
        for i, medicamento in enumerate(medicamentos):
            if medicamento.strip():
                tiene_medicamentos = True
                prescripcion = Prescripcion(
                    consulta_id=consulta.id,
                    medicamento=medicamento.strip(),
                    dosis=dosis_list[i].strip() if i < len(dosis_list) else '',
                    frecuencia=frecuencias[i].strip() if i < len(frecuencias) else '',
                    duracion_dias=int(duraciones[i]) if i < len(duraciones) and duraciones[i] else None,
                    via_administracion='Oral'
                )
                db.session.add(prescripcion)
        
        if tiene_medicamentos:
            consulta.estado = 'completada'
            db.session.commit()
            flash('Consulta completada exitosamente con resultados del hospital.', 'success')
        else:
            flash('Debes agregar al menos un medicamento para completar la consulta.', 'warning')
        
        return redirect(url_for('consultas.ver', id=id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al completar consulta: {str(e)}', 'danger')
        return redirect(url_for('consultas.ver', id=id))


@consultas_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar consulta"""
    from models import db, Consulta
    
    cons = Consulta.query.get_or_404(id)
    
    if cons.usuario_id != current_user.id and not current_user.is_admin:
        flash('No tiene permisos para editar esta consulta.', 'danger')
        return redirect(url_for('consultas.ver', id=id))
    
    if cons.estado == 'completada':
        flash('No se puede editar una consulta completada.', 'warning')
        return redirect(url_for('consultas.ver', id=id))
    
    if request.method == 'POST':
        try:
            # Campos que todos pueden editar
            cons.motivo_consulta = request.form.get('motivo_consulta', '').strip()
            cons.presion_arterial = request.form.get('presion_arterial', '').strip() or None
            cons.frecuencia_cardiaca = request.form.get('frecuencia_cardiaca', type=int)
            cons.temperatura = request.form.get('temperatura', type=float)
            cons.frecuencia_respiratoria = request.form.get('frecuencia_respiratoria', type=int)
            cons.saturacion_oxigeno = request.form.get('saturacion_oxigeno', type=int)
            cons.peso = request.form.get('peso', type=float)
            cons.talla = request.form.get('talla', type=float)
            cons.examen_fisico = request.form.get('examen_fisico', '').strip() or None
            
            # Solo médicos/admins pueden editar estos campos
            if current_user.can_complete_consulta():
                cons.diagnostico = request.form.get('diagnostico', '').strip() or None
                cons.plan_tratamiento = request.form.get('plan_tratamiento', '').strip() or None
                cons.indicaciones = request.form.get('indicaciones', '').strip() or None
                cons.observaciones = request.form.get('observaciones', '').strip() or None
            
            db.session.commit()
            flash('Consulta actualizada exitosamente.', 'success')
            return redirect(url_for('consultas.ver', id=cons.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar consulta: {str(e)}', 'danger')
    
    return render_template('consultas/editar.html', consulta=cons)


@consultas_bp.route('/signos-vitales/<int:estudiante_id>', methods=['GET', 'POST'])
@login_required
def registrar_signos(estudiante_id):
    """Registrar solo signos vitales (para enfermeras)"""
    from models import db, Estudiante, Consulta
    
    est = Estudiante.query.get_or_404(estudiante_id)
    
    if request.method == 'POST':
        try:
            nueva_consulta = Consulta(
                estudiante_id=est.id,
                usuario_id=current_user.id,
                motivo_consulta=request.form.get('motivo_consulta', 'Control de signos vitales'),
                presion_arterial=request.form.get('presion_arterial', '').strip() or None,
                frecuencia_cardiaca=request.form.get('frecuencia_cardiaca', type=int),
                temperatura=request.form.get('temperatura', type=float),
                frecuencia_respiratoria=request.form.get('frecuencia_respiratoria', type=int),
                saturacion_oxigeno=request.form.get('saturacion_oxigeno', type=int),
                peso=request.form.get('peso', type=float),
                talla=request.form.get('talla', type=float),
                examen_fisico=request.form.get('examen_fisico', '').strip() or None,
                estado='pendiente',
                observaciones='Registro de signos vitales por enfermería'
            )
            
            db.session.add(nueva_consulta)
            db.session.commit()
            
            flash(f'Signos vitales registrados para {est.nombre_completo}. Consulta pendiente de atención médica.', 'success')
            return redirect(url_for('estudiantes.ficha', id=est.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('consultas/signos_vitales.html', estudiante=est)