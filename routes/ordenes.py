from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime

ordenes_bp = Blueprint('ordenes', __name__, url_prefix='/ordenes')

# Configuración de archivos permitidos
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'bmp', 'webp'}
UPLOAD_FOLDER = 'static/uploads/resultados'
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@ordenes_bp.route('/')
@login_required
def lista():
    """Lista de órdenes de referencia"""
    from models import OrdenReferencia
    
    estado = request.args.get('estado', 'todas')
    
    query = OrdenReferencia.query
    
    if estado != 'todas':
        query = query.filter_by(estado=estado)
    
    ordenes = query.order_by(OrdenReferencia.fecha_emision.desc()).all()
    
    return render_template('ordenes/lista.html', 
                         ordenes=ordenes,
                         estado_actual=estado)


@ordenes_bp.route('/nueva/<int:consulta_id>', methods=['GET', 'POST'])
@login_required
def nueva(consulta_id):
    """Generar nueva orden de referencia - SOLO MÉDICOS Y ADMINS"""
    from models import db, Consulta, OrdenReferencia
    import qrcode
    
    # BLOQUEAR ACCESO A ENFERMERAS
    if not current_user.can_create_orden():
        flash('No tienes permisos para crear órdenes de referencia. Solo los médicos pueden crear órdenes.', 'danger')
        return redirect(url_for('consultas.lista'))
    
    consulta = Consulta.query.get_or_404(consulta_id)
    
    if request.method == 'POST':
        try:
            tipo_atencion = request.form.get('tipo_atencion', '').strip()
            especialidad = request.form.get('especialidad', '').strip()
            diagnostico = request.form.get('diagnostico_presuntivo', '').strip()
            motivo = request.form.get('motivo_referencia', '').strip()
            prioridad = request.form.get('prioridad', 'normal')
            
            if not all([tipo_atencion, diagnostico, motivo]):
                flash('Por favor complete todos los campos obligatorios.', 'warning')
                return render_template('ordenes/nueva.html', consulta=consulta)
            
            orden = OrdenReferencia(
                consulta_id=consulta.id,
                estudiante_id=consulta.estudiante_id,
                medico_id=current_user.id,
                tipo_atencion=tipo_atencion,
                especialidad=especialidad,
                diagnostico_presuntivo=diagnostico,
                motivo_referencia=motivo,
                prioridad=prioridad
            )
            
            orden.generar_codigo_qr()
            
            # CAMBIAR ESTADO DE CONSULTA A "EN_REFERENCIA"
            consulta.estado = 'en_referencia'
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(f"{request.url_root}ordenes/qr/{orden.codigo_qr}")
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            qr_folder = 'static/qr_codes'
            os.makedirs(qr_folder, exist_ok=True)
            qr_path = os.path.join(qr_folder, f'{orden.codigo_qr}.png')
            img.save(qr_path)
            
            db.session.add(orden)
            db.session.commit()
            
            flash('Orden de referencia generada exitosamente. La consulta está en estado "En Referencia".', 'success')
            return redirect(url_for('ordenes.ver', id=orden.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al generar orden: {str(e)}', 'danger')
    
    return render_template('ordenes/nueva.html', consulta=consulta)


@ordenes_bp.route('/<int:id>')
@login_required
def ver(id):
    """Ver detalles de una orden"""
    from models import OrdenReferencia
    
    orden = OrdenReferencia.query.get_or_404(id)
    return render_template('ordenes/ver.html', orden=orden)


@ordenes_bp.route('/descargar-qr/<int:id>')
@login_required
def descargar_qr(id):
    """Descargar código QR de la orden"""
    from models import OrdenReferencia
    
    orden = OrdenReferencia.query.get_or_404(id)
    qr_path = f'static/qr_codes/{orden.codigo_qr}.png'
    
    if not os.path.exists(qr_path):
        flash('Código QR no encontrado.', 'danger')
        return redirect(url_for('ordenes.ver', id=id))
    
    return send_file(qr_path, 
                     as_attachment=True,
                     download_name=f'QR_{orden.codigo_qr}.png')


@ordenes_bp.route('/qr/<codigo>')
def ver_qr(codigo):
    """Ver orden mediante código QR (acceso público para hospitales)"""
    from models import OrdenReferencia
    
    orden = OrdenReferencia.query.filter_by(codigo_qr=codigo).first()
    
    if not orden:
        return render_template('errors/404.html'), 404
    
    return render_template('ordenes/ver_hospital.html', orden=orden)


@ordenes_bp.route('/marcar-presentada/<codigo>', methods=['POST'])
def marcar_presentada(codigo):
    """Marcar orden como presentada en hospital"""
    from models import db, OrdenReferencia, get_bolivia_time
    
    orden = OrdenReferencia.query.filter_by(codigo_qr=codigo).first_or_404()
    
    if orden.estado == 'pendiente':
        orden.estado = 'presentada'
        orden.fecha_presentacion_hospital = get_bolivia_time()
        db.session.commit()
        flash('Orden marcada como presentada en hospital.', 'success')
    
    return redirect(url_for('ordenes.ver_qr', codigo=codigo))


@ordenes_bp.route('/registrar-atencion/<codigo>', methods=['POST'])
def registrar_atencion(codigo):
    """Registrar atención completada con resultados e imágenes"""
    from models import db, OrdenReferencia, ImagenOrden, get_bolivia_time
    
    orden = OrdenReferencia.query.filter_by(codigo_qr=codigo).first_or_404()
    
    try:
        # Registrar resultados
        orden.diagnostico_hospital = request.form.get('diagnostico_hospital', '').strip()
        orden.tratamiento_aplicado = request.form.get('tratamiento_aplicado', '').strip()
        orden.resultado = request.form.get('resultado', '').strip()
        orden.observaciones_hospital = request.form.get('observaciones_hospital', '').strip()
        orden.estado = 'completada'
        orden.fecha_completada = get_bolivia_time()
        
        # Procesar imágenes subidas
        if 'imagenes' in request.files:
            files = request.files.getlist('imagenes')
            
            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    # Crear carpeta si no existe
                    upload_path = os.path.join(UPLOAD_FOLDER, str(orden.id))
                    os.makedirs(upload_path, exist_ok=True)
                    
                    # Generar nombre único
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = secure_filename(file.filename)
                    nombre_unico = f"{timestamp}_{filename}"
                    file_path = os.path.join(upload_path, nombre_unico)
                    
                    # Guardar archivo
                    file.save(file_path)
                    
                    # Registrar en base de datos
                    tipo_imagen = request.form.get(f'tipo_imagen_{files.index(file)}', 'resultado')
                    descripcion = request.form.get(f'descripcion_{files.index(file)}', '')
                    
                    imagen = ImagenOrden(
                        orden_id=orden.id,
                        nombre_archivo=filename,
                        ruta_archivo=file_path,
                        tipo_imagen=tipo_imagen,
                        descripcion=descripcion
                    )
                    db.session.add(imagen)
        
        db.session.commit()
        flash('Atención registrada exitosamente. La orden está completada y disponible para que el médico complete la consulta.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al registrar atención: {str(e)}', 'danger')
    
    return redirect(url_for('ordenes.ver_qr', codigo=codigo))


@ordenes_bp.route('/imagen/<int:imagen_id>')
@login_required
def ver_imagen(imagen_id):
    """Ver imagen adjunta"""
    from models import ImagenOrden
    
    imagen = ImagenOrden.query.get_or_404(imagen_id)
    
    if not os.path.exists(imagen.ruta_archivo):
        abort(404)
    
    return send_file(imagen.ruta_archivo)


@ordenes_bp.route('/eliminar-imagen/<int:imagen_id>', methods=['POST'])
@login_required
def eliminar_imagen(imagen_id):
    """Eliminar imagen adjunta"""
    from models import db, ImagenOrden
    
    imagen = ImagenOrden.query.get_or_404(imagen_id)
    orden_id = imagen.orden_id
    
    try:
        # Eliminar archivo físico
        if os.path.exists(imagen.ruta_archivo):
            os.remove(imagen.ruta_archivo)
        
        # Eliminar registro
        db.session.delete(imagen)
        db.session.commit()
        
        flash('Imagen eliminada exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar imagen: {str(e)}', 'danger')
    
    return redirect(url_for('ordenes.ver', id=orden_id))