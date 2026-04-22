from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime, date, timezone, timedelta
import secrets

db = SQLAlchemy()

# Zona horaria de Bolivia (UTC-4)
BOLIVIA_TZ = timezone(timedelta(hours=-4))

def get_bolivia_time():
    """Retorna la hora actual de Bolivia (UTC-4)"""
    return datetime.now(BOLIVIA_TZ)


class Usuario(UserMixin, db.Model):
    """Modelo de Usuario del Sistema"""
    
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre_completo = db.Column(db.String(150), nullable=False)
    rol = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    activo = db.Column(db.Boolean, default=True, nullable=False)
    ultimo_acceso = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=get_bolivia_time, nullable=False)
    
    consultas_registradas = db.relationship('Consulta', backref='usuario', lazy='dynamic')
    ordenes_generadas = db.relationship('OrdenReferencia', backref='medico', lazy='dynamic')
    
    def __repr__(self):
        return f'<Usuario {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def update_last_access(self):
        self.ultimo_acceso = get_bolivia_time()
        db.session.commit()
    
    @property
    def is_admin(self):
        return self.rol == 'admin'
    
    @property
    def is_medico(self):
        return self.rol == 'medico'
    
    @property
    def is_enfermera(self):
        return self.rol == 'enfermera'
    
    def can_register_consulta(self):
        """Enfermeras, médicos y admins pueden registrar consultas"""
        return self.rol in ['admin', 'medico', 'enfermera']
    
    def can_complete_consulta(self):
        """Solo médicos y admins pueden completar consultas (diagnosticar, prescribir)"""
        return self.rol in ['admin', 'medico']
    
    def can_create_orden(self):
        """Solo médicos y admins pueden crear órdenes de referencia"""
        return self.rol in ['admin', 'medico']


class Estudiante(db.Model):
    """Modelo de Estudiante (Paciente)"""
    
    __tablename__ = 'estudiantes'
    
    id = db.Column(db.Integer, primary_key=True)
    ci = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido_paterno = db.Column(db.String(100), nullable=False)
    apellido_materno = db.Column(db.String(100))
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    sexo = db.Column(db.String(1), nullable=False)
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    carrera = db.Column(db.String(100), nullable=False)
    matricula = db.Column(db.String(50), unique=True, nullable=False, index=True)
    semestre = db.Column(db.Integer)
    grupo_sanguineo = db.Column(db.String(5))
    alergias = db.Column(db.Text)
    enfermedades_cronicas = db.Column(db.Text)
    cirugias_previas = db.Column(db.Text)
    medicamentos_actuales = db.Column(db.Text)
    contacto_emergencia_nombre = db.Column(db.String(150))
    contacto_emergencia_telefono = db.Column(db.String(20))
    contacto_emergencia_relacion = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=get_bolivia_time, nullable=False)
    updated_at = db.Column(db.DateTime, default=get_bolivia_time, onupdate=get_bolivia_time)
    
    consultas = db.relationship('Consulta', backref='estudiante', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Estudiante {self.nombre_completo}>'
    
    @property
    def nombre_completo(self):
        if self.apellido_materno:
            return f"{self.apellido_paterno} {self.apellido_materno}, {self.nombre}"
        return f"{self.apellido_paterno}, {self.nombre}"
    
    @property
    def edad(self):
        if not self.fecha_nacimiento:
            return 0
        today = date.today()
        edad = today.year - self.fecha_nacimiento.year
        if today.month < self.fecha_nacimiento.month or \
           (today.month == self.fecha_nacimiento.month and today.day < self.fecha_nacimiento.day):
            edad -= 1
        return edad
    
    def fecha_nacimiento_formato(self):
        """Retorna la fecha en formato YYYY-MM-DD para inputs HTML"""
        if self.fecha_nacimiento:
            return self.fecha_nacimiento.strftime('%Y-%m-%d')
        return ''
    
    @property
    def tiene_alergias(self):
        return bool(self.alergias and self.alergias.strip())
    
    @property
    def tiene_enfermedades_cronicas(self):
        return bool(self.enfermedades_cronicas and self.enfermedades_cronicas.strip())
    
    def get_ultima_consulta(self):
        return self.consultas.order_by(db.desc('fecha_hora')).first()
    
    def get_total_consultas(self):
        return self.consultas.count()
    
    def to_dict(self):
        return {
            'id': self.id,
            'ci': self.ci,
            'nombre_completo': self.nombre_completo,
            'edad': self.edad,
            'carrera': self.carrera,
            'matricula': self.matricula,
            'telefono': self.telefono,
            'grupo_sanguineo': self.grupo_sanguineo,
            'alergias': self.alergias,
            'total_consultas': self.get_total_consultas()
        }


class Consulta(db.Model):
    """Modelo de Consulta Médica"""
    
    __tablename__ = 'consultas'
    
    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('estudiantes.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_hora = db.Column(db.DateTime, default=get_bolivia_time, nullable=False, index=True)
    estado = db.Column(db.String(20), default='pendiente', nullable=False, index=True)
    motivo_consulta = db.Column(db.Text, nullable=False)
    presion_arterial = db.Column(db.String(20))
    frecuencia_cardiaca = db.Column(db.Integer)
    temperatura = db.Column(db.Float)
    frecuencia_respiratoria = db.Column(db.Integer)
    saturacion_oxigeno = db.Column(db.Integer)
    peso = db.Column(db.Float)
    talla = db.Column(db.Float)
    examen_fisico = db.Column(db.Text)
    diagnostico = db.Column(db.Text)
    plan_tratamiento = db.Column(db.Text)
    indicaciones = db.Column(db.Text)
    observaciones = db.Column(db.Text)
    
    prescripciones = db.relationship('Prescripcion', backref='consulta', lazy='dynamic', cascade='all, delete-orphan')
    orden_referencia = db.relationship('OrdenReferencia', backref='consulta', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Consulta {self.id}>'
    
    @property
    def fecha_formateada(self):
        return self.fecha_hora.strftime('%d/%m/%Y %H:%M')
    
    @property
    def color_estado(self):
        colores = {
            'pendiente': 'warning',
            'en_referencia': 'info',
            'completada': 'success'
        }
        return colores.get(self.estado, 'secondary')
    
    @property
    def icono_estado(self):
        iconos = {
            'pendiente': 'clock',
            'en_referencia': 'hospital',
            'completada': 'check-circle'
        }
        return iconos.get(self.estado, 'circle')
    
    @property
    def estado_texto(self):
        textos = {
            'pendiente': 'Pendiente',
            'en_referencia': 'En Referencia',
            'completada': 'Completada'
        }
        return textos.get(self.estado, self.estado)
    
    @property
    def imc(self):
        if self.peso and self.talla and self.talla > 0:
            talla_mts = self.talla / 100
            return round(self.peso / (talla_mts ** 2), 2)
        return None
    
    @property
    def clasificacion_imc(self):
        imc = self.imc
        if not imc:
            return None
        if imc < 18.5:
            return 'Bajo peso'
        elif imc < 25:
            return 'Normal'
        elif imc < 30:
            return 'Sobrepeso'
        else:
            return 'Obesidad'


class Prescripcion(db.Model):
    """Modelo de Prescripción"""
    
    __tablename__ = 'prescripciones'
    
    id = db.Column(db.Integer, primary_key=True)
    consulta_id = db.Column(db.Integer, db.ForeignKey('consultas.id'), nullable=False)
    medicamento = db.Column(db.String(200), nullable=False)
    dosis = db.Column(db.String(100), nullable=False)
    frecuencia = db.Column(db.String(100), nullable=False)
    duracion_dias = db.Column(db.Integer)
    via_administracion = db.Column(db.String(50))
    indicaciones_especiales = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Prescripcion {self.medicamento}>'


class OrdenReferencia(db.Model):
    """Modelo de Orden de Referencia"""
    
    __tablename__ = 'ordenes_referencia'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo_qr = db.Column(db.String(50), unique=True, nullable=False, index=True)
    consulta_id = db.Column(db.Integer, db.ForeignKey('consultas.id'), nullable=False)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('estudiantes.id'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    tipo_atencion = db.Column(db.String(100), nullable=False)
    especialidad = db.Column(db.String(100))
    diagnostico_presuntivo = db.Column(db.Text, nullable=False)
    motivo_referencia = db.Column(db.Text, nullable=False)
    prioridad = db.Column(db.String(20), default='normal')
    estado = db.Column(db.String(20), default='pendiente', nullable=False)
    fecha_emision = db.Column(db.DateTime, default=get_bolivia_time, nullable=False)
    fecha_presentacion_hospital = db.Column(db.DateTime)
    fecha_completada = db.Column(db.DateTime)
    diagnostico_hospital = db.Column(db.Text)
    tratamiento_aplicado = db.Column(db.Text)
    resultado = db.Column(db.Text)
    observaciones_hospital = db.Column(db.Text)
    
    estudiante = db.relationship('Estudiante', backref='ordenes_referencia')
    imagenes = db.relationship('ImagenOrden', backref='orden', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<OrdenReferencia {self.codigo_qr}>'
    
    def generar_codigo_qr(self):
        self.codigo_qr = f"APSA-{secrets.token_hex(4).upper()}"
        return self.codigo_qr
    
    @property
    def color_estado(self):
        colores = {
            'pendiente': 'warning',
            'presentada': 'info',
            'completada': 'success',
            'cancelada': 'secondary'
        }
        return colores.get(self.estado, 'secondary')
    
    @property
    def icono_estado(self):
        iconos = {
            'pendiente': 'clock',
            'presentada': 'hospital',
            'completada': 'check-circle',
            'cancelada': 'x-circle'
        }
        return iconos.get(self.estado, 'circle')
    
    @property
    def color_prioridad(self):
        return 'danger' if self.prioridad == 'urgente' else 'info'
    
    @property
    def dias_desde_emision(self):
        """Calcula días desde la emisión de la orden"""
        ahora = get_bolivia_time()
        if self.fecha_emision.tzinfo is None:
            fecha_emision_con_tz = self.fecha_emision.replace(tzinfo=BOLIVIA_TZ)
        else:
            fecha_emision_con_tz = self.fecha_emision
        return (ahora - fecha_emision_con_tz).days


class ImagenOrden(db.Model):
    """Modelo para almacenar imágenes adjuntas a órdenes de referencia"""
    
    __tablename__ = 'imagenes_ordenes'
    
    id = db.Column(db.Integer, primary_key=True)
    orden_id = db.Column(db.Integer, db.ForeignKey('ordenes_referencia.id'), nullable=False)
    nombre_archivo = db.Column(db.String(255), nullable=False)
    ruta_archivo = db.Column(db.String(500), nullable=False)
    tipo_imagen = db.Column(db.String(50))
    descripcion = db.Column(db.Text)
    fecha_subida = db.Column(db.DateTime, default=get_bolivia_time, nullable=False)
    
    def __repr__(self):
        return f'<ImagenOrden {self.nombre_archivo}>'