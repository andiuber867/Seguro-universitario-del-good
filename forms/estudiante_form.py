from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, IntegerField, TextAreaField, SubmitField, EmailField
from wtforms.validators import DataRequired, Length, Email, Optional, NumberRange, Regexp


class EstudianteForm(FlaskForm):
    """Formulario para registrar/editar estudiante"""
    
    # Datos básicos
    ci = StringField(
        'Cédula de Identidad (CI)',
        validators=[
            DataRequired(message='El CI es obligatorio'),
            Length(min=5, max=20, message='CI inválido'),
            Regexp(r'^[0-9]+$', message='El CI solo debe contener números')
        ],
        render_kw={
            'placeholder': 'Ej: 12345678',
            'class': 'form-control'
        }
    )
    
    nombre = StringField(
        'Nombre(s)',
        validators=[
            DataRequired(message='El nombre es obligatorio'),
            Length(min=2, max=100, message='El nombre debe tener entre 2 y 100 caracteres')
        ],
        render_kw={
            'placeholder': 'Ej: Juan Carlos',
            'class': 'form-control'
        }
    )
    
    apellido_paterno = StringField(
        'Apellido Paterno',
        validators=[
            DataRequired(message='El apellido paterno es obligatorio'),
            Length(min=2, max=100, message='El apellido debe tener entre 2 y 100 caracteres')
        ],
        render_kw={
            'placeholder': 'Ej: Pérez',
            'class': 'form-control'
        }
    )
    
    apellido_materno = StringField(
        'Apellido Materno',
        validators=[
            Optional(),
            Length(max=100, message='El apellido debe tener máximo 100 caracteres')
        ],
        render_kw={
            'placeholder': 'Ej: García',
            'class': 'form-control'
        }
    )
    
    fecha_nacimiento = DateField(
        'Fecha de Nacimiento',
        validators=[
            DataRequired(message='La fecha de nacimiento es obligatoria')
        ],
        format='%Y-%m-%d',
        render_kw={
            'class': 'form-control',
            'type': 'date'
        }
    )
    
    sexo = SelectField(
        'Sexo',
        choices=[
            ('', 'Seleccione...'),
            ('M', 'Masculino'),
            ('F', 'Femenino')
        ],
        validators=[
            DataRequired(message='El sexo es obligatorio')
        ],
        render_kw={
            'class': 'form-select'
        }
    )
    
    # Datos de contacto
    direccion = StringField(
        'Dirección',
        validators=[
            Optional(),
            Length(max=200)
        ],
        render_kw={
            'placeholder': 'Ej: Av. Cristo Redentor #123',
            'class': 'form-control'
        }
    )
    
    telefono = StringField(
        'Teléfono',
        validators=[
            Optional(),
            Length(min=7, max=20, message='Teléfono inválido')
        ],
        render_kw={
            'placeholder': 'Ej: 77123456',
            'class': 'form-control'
        }
    )
    
    email = EmailField(
        'Correo Electrónico',
        validators=[
            Optional(),
            Email(message='Correo electrónico inválido')
        ],
        render_kw={
            'placeholder': 'ejemplo@correo.com',
            'class': 'form-control'
        }
    )
    
    # Información académica
    carrera = SelectField(
        'Carrera',
        choices=[
            ('', 'Seleccione carrera...'),
            ('Ingeniería de Sistemas', 'Ingeniería de Sistemas'),
            ('Ingeniería Agronómica', 'Ingeniería Agronómica'),
            ('Ingeniería Forestal', 'Ingeniería Forestal'),
            ('Medicina Veterinaria y Zootecnia', 'Medicina Veterinaria y Zootecnia'),
            ('Administración de Empresas', 'Administración de Empresas'),
            ('Contaduría Pública', 'Contaduría Pública'),
            ('Derecho', 'Derecho'),
            ('Biología', 'Biología'),
            ('Otra', 'Otra')
        ],
        validators=[
            DataRequired(message='La carrera es obligatoria')
        ],
        render_kw={
            'class': 'form-select'
        }
    )
    
    matricula = StringField(
        'Número de Matrícula',
        validators=[
            DataRequired(message='La matrícula es obligatoria'),
            Length(min=5, max=50, message='Matrícula inválida')
        ],
        render_kw={
            'placeholder': 'Ej: 218123456',
            'class': 'form-control'
        }
    )
    
    semestre = IntegerField(
        'Semestre',
        validators=[
            Optional(),
            NumberRange(min=1, max=12, message='Semestre debe estar entre 1 y 12')
        ],
        render_kw={
            'placeholder': 'Ej: 5',
            'class': 'form-control',
            'min': '1',
            'max': '12'
        }
    )
    
    # Información médica
    grupo_sanguineo = SelectField(
        'Grupo Sanguíneo',
        choices=[
            ('', 'Seleccione...'),
            ('O+', 'O+'),
            ('O-', 'O-'),
            ('A+', 'A+'),
            ('A-', 'A-'),
            ('B+', 'B+'),
            ('B-', 'B-'),
            ('AB+', 'AB+'),
            ('AB-', 'AB-')
        ],
        validators=[Optional()],
        render_kw={
            'class': 'form-select'
        }
    )
    
    alergias = TextAreaField(
        'Alergias',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Ej: Penicilina, mariscos, polen...',
            'class': 'form-control',
            'rows': '3'
        }
    )
    
    enfermedades_cronicas = TextAreaField(
        'Enfermedades Crónicas',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Ej: Diabetes, hipertensión, asma...',
            'class': 'form-control',
            'rows': '3'
        }
    )
    
    cirugias_previas = TextAreaField(
        'Cirugías Previas',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Describa cirugías anteriores si las hubo...',
            'class': 'form-control',
            'rows': '2'
        }
    )
    
    medicamentos_actuales = TextAreaField(
        'Medicamentos que Toma Actualmente',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Liste medicamentos que toma regularmente...',
            'class': 'form-control',
            'rows': '2'
        }
    )
    
    # Contacto de emergencia
    contacto_emergencia_nombre = StringField(
        'Nombre del Contacto de Emergencia',
        validators=[
            Optional(),
            Length(max=150)
        ],
        render_kw={
            'placeholder': 'Ej: María López',
            'class': 'form-control'
        }
    )
    
    contacto_emergencia_telefono = StringField(
        'Teléfono de Emergencia',
        validators=[
            Optional(),
            Length(min=7, max=20)
        ],
        render_kw={
            'placeholder': 'Ej: 77123456',
            'class': 'form-control'
        }
    )
    
    contacto_emergencia_relacion = StringField(
        'Relación',
        validators=[
            Optional(),
            Length(max=50)
        ],
        render_kw={
            'placeholder': 'Ej: Madre, Hermano, Esposo/a...',
            'class': 'form-control'
        }
    )
    
    submit = SubmitField(
        'Guardar Estudiante',
        render_kw={
            'class': 'btn btn-primary btn-lg'
        }
    )