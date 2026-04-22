from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, FloatField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange, Length


class ConsultaForm(FlaskForm):
    """Formulario para registrar consulta médica"""
    
    # Motivo de consulta
    motivo_consulta = TextAreaField(
        'Motivo de Consulta',
        validators=[
            DataRequired(message='El motivo de consulta es obligatorio'),
            Length(min=10, message='Describa el motivo con más detalle (mínimo 10 caracteres)')
        ],
        render_kw={
            'placeholder': 'Describa detalladamente el motivo de la consulta...',
            'class': 'form-control',
            'rows': '3'
        }
    )
    
    # Signos vitales
    presion_arterial = StringField(
        'Presión Arterial',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Ej: 120/80',
            'class': 'form-control'
        }
    )
    
    frecuencia_cardiaca = IntegerField(
        'Frecuencia Cardíaca (lat/min)',
        validators=[
            Optional(),
            NumberRange(min=30, max=250, message='Valor fuera de rango normal (30-250)')
        ],
        render_kw={
            'placeholder': 'Ej: 72',
            'class': 'form-control',
            'min': '30',
            'max': '250'
        }
    )
    
    temperatura = FloatField(
        'Temperatura (°C)',
        validators=[
            Optional(),
            NumberRange(min=32.0, max=45.0, message='Valor fuera de rango (32-45°C)')
        ],
        render_kw={
            'placeholder': 'Ej: 36.5',
            'class': 'form-control',
            'step': '0.1',
            'min': '32',
            'max': '45'
        }
    )
    
    frecuencia_respiratoria = IntegerField(
        'Frecuencia Respiratoria (resp/min)',
        validators=[
            Optional(),
            NumberRange(min=8, max=60, message='Valor fuera de rango (8-60)')
        ],
        render_kw={
            'placeholder': 'Ej: 18',
            'class': 'form-control',
            'min': '8',
            'max': '60'
        }
    )
    
    saturacion_oxigeno = IntegerField(
        'Saturación de Oxígeno (%)',
        validators=[
            Optional(),
            NumberRange(min=70, max=100, message='Valor fuera de rango (70-100%)')
        ],
        render_kw={
            'placeholder': 'Ej: 98',
            'class': 'form-control',
            'min': '70',
            'max': '100'
        }
    )
    
    peso = FloatField(
        'Peso (kg)',
        validators=[
            Optional(),
            NumberRange(min=20.0, max=250.0, message='Valor fuera de rango (20-250 kg)')
        ],
        render_kw={
            'placeholder': 'Ej: 70.5',
            'class': 'form-control',
            'step': '0.1',
            'min': '20',
            'max': '250'
        }
    )
    
    talla = FloatField(
        'Talla (cm)',
        validators=[
            Optional(),
            NumberRange(min=100.0, max=250.0, message='Valor fuera de rango (100-250 cm)')
        ],
        render_kw={
            'placeholder': 'Ej: 170',
            'class': 'form-control',
            'step': '0.1',
            'min': '100',
            'max': '250'
        }
    )
    
    # Examen físico y diagnóstico
    examen_fisico = TextAreaField(
        'Examen Físico',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Describa los hallazgos del examen físico...',
            'class': 'form-control',
            'rows': '4'
        }
    )
    
    diagnostico = TextAreaField(
        'Diagnóstico',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Indique el diagnóstico o impresión diagnóstica...',
            'class': 'form-control',
            'rows': '3'
        }
    )
    
    plan_tratamiento = TextAreaField(
        'Plan de Tratamiento',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Describa el plan de tratamiento recomendado...',
            'class': 'form-control',
            'rows': '3'
        }
    )
    
    indicaciones = TextAreaField(
        'Indicaciones al Paciente',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Indicaciones y recomendaciones para el paciente...',
            'class': 'form-control',
            'rows': '3'
        }
    )
    
    observaciones = TextAreaField(
        'Observaciones Adicionales',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Cualquier observación adicional relevante...',
            'class': 'form-control',
            'rows': '2'
        }
    )
    
    submit = SubmitField(
        'Guardar Consulta',
        render_kw={
            'class': 'btn btn-success btn-lg'
        }
    )


class SignosVitalesForm(FlaskForm):
    """Formulario simplificado para registrar solo signos vitales (enfermeras)"""
    
    motivo_consulta = TextAreaField(
        'Motivo Breve',
        validators=[
            DataRequired(message='Indique brevemente el motivo')
        ],
        render_kw={
            'placeholder': 'Ej: Control de rutina, chequeo general...',
            'class': 'form-control',
            'rows': '2'
        }
    )
    
    presion_arterial = StringField(
        'Presión Arterial',
        validators=[
            DataRequired(message='La presión arterial es obligatoria')
        ],
        render_kw={
            'placeholder': 'Ej: 120/80',
            'class': 'form-control'
        }
    )
    
    frecuencia_cardiaca = IntegerField(
        'Frecuencia Cardíaca',
        validators=[
            DataRequired(message='La frecuencia cardíaca es obligatoria'),
            NumberRange(min=30, max=250)
        ],
        render_kw={
            'placeholder': 'lat/min',
            'class': 'form-control'
        }
    )
    
    temperatura = FloatField(
        'Temperatura',
        validators=[
            DataRequired(message='La temperatura es obligatoria'),
            NumberRange(min=32.0, max=45.0)
        ],
        render_kw={
            'placeholder': '°C',
            'class': 'form-control',
            'step': '0.1'
        }
    )
    
    frecuencia_respiratoria = IntegerField(
        'Frecuencia Respiratoria',
        validators=[
            Optional(),
            NumberRange(min=8, max=60)
        ],
        render_kw={
            'placeholder': 'resp/min',
            'class': 'form-control'
        }
    )
    
    saturacion_oxigeno = IntegerField(
        'Saturación O₂',
        validators=[
            Optional(),
            NumberRange(min=70, max=100)
        ],
        render_kw={
            'placeholder': '%',
            'class': 'form-control'
        }
    )
    
    peso = FloatField(
        'Peso',
        validators=[Optional()],
        render_kw={
            'placeholder': 'kg',
            'class': 'form-control',
            'step': '0.1'
        }
    )
    
    talla = FloatField(
        'Talla',
        validators=[Optional()],
        render_kw={
            'placeholder': 'cm',
            'class': 'form-control',
            'step': '0.1'
        }
    )
    
    submit = SubmitField(
        'Registrar Signos Vitales',
        render_kw={
            'class': 'btn btn-primary btn-lg'
        }
    )


class OrdenReferenciaForm(FlaskForm):
    """Formulario para generar orden de referencia"""
    
    tipo_atencion = SelectField(
        'Tipo de Atención',
        choices=[
            ('', 'Seleccione tipo...'),
            ('consulta', 'Consulta Médica Especializada'),
            ('laboratorio', 'Exámenes de Laboratorio'),
            ('imagen', 'Estudios de Imagen'),
            ('procedimiento', 'Procedimiento Médico'),
            ('urgencia', 'Atención de Urgencia')
        ],
        validators=[
            DataRequired(message='Seleccione el tipo de atención')
        ],
        render_kw={
            'class': 'form-select'
        }
    )
    
    especialidad = StringField(
        'Especialidad',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Ej: Cardiología, Traumatología, Dermatología...',
            'class': 'form-control'
        }
    )
    
    diagnostico_presuntivo = TextAreaField(
        'Diagnóstico Presuntivo',
        validators=[
            DataRequired(message='El diagnóstico presuntivo es obligatorio'),
            Length(min=10, message='Describa el diagnóstico con más detalle')
        ],
        render_kw={
            'placeholder': 'Describa el diagnóstico o sospecha diagnóstica...',
            'class': 'form-control',
            'rows': '3'
        }
    )
    
    motivo_referencia = TextAreaField(
        'Motivo de Referencia',
        validators=[
            DataRequired(message='El motivo de referencia es obligatorio'),
            Length(min=10, message='Explique detalladamente el motivo')
        ],
        render_kw={
            'placeholder': 'Explique por qué se refiere al hospital...',
            'class': 'form-control',
            'rows': '4'
        }
    )
    
    prioridad = SelectField(
        'Prioridad',
        choices=[
            ('normal', 'Normal'),
            ('urgente', 'Urgente')
        ],
        validators=[
            DataRequired()
        ],
        render_kw={
            'class': 'form-select'
        }
    )
    
    submit = SubmitField(
        'Generar Orden de Referencia',
        render_kw={
            'class': 'btn btn-danger btn-lg'
        }
    )