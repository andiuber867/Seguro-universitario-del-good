from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    """Formulario de inicio de sesión"""
    
    username = StringField(
        'Usuario',
        validators=[
            DataRequired(message='El usuario es obligatorio'),
            Length(min=3, max=50, message='El usuario debe tener entre 3 y 50 caracteres')
        ],
        render_kw={
            'placeholder': 'Ingrese su usuario',
            'class': 'form-control',
            'autocomplete': 'username',
            'autofocus': True
        }
    )
    
    password = PasswordField(
        'Contraseña',
        validators=[
            DataRequired(message='La contraseña es obligatoria')
        ],
        render_kw={
            'placeholder': 'Ingrese su contraseña',
            'class': 'form-control',
            'autocomplete': 'current-password'
        }
    )
    
    remember = BooleanField(
        'Recordarme',
        render_kw={
            'class': 'form-check-input'
        }
    )
    
    submit = SubmitField(
        'Iniciar Sesión',
        render_kw={
            'class': 'btn btn-primary btn-block w-100'
        }
    )


class CambiarPasswordForm(FlaskForm):
    """Formulario para cambiar contraseña"""
    
    password_actual = PasswordField(
        'Contraseña Actual',
        validators=[
            DataRequired(message='Ingrese su contraseña actual')
        ],
        render_kw={
            'placeholder': 'Contraseña actual',
            'class': 'form-control'
        }
    )
    
    password_nueva = PasswordField(
        'Nueva Contraseña',
        validators=[
            DataRequired(message='Ingrese la nueva contraseña'),
            Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
        ],
        render_kw={
            'placeholder': 'Nueva contraseña (mínimo 6 caracteres)',
            'class': 'form-control'
        }
    )
    
    password_confirmar = PasswordField(
        'Confirmar Nueva Contraseña',
        validators=[
            DataRequired(message='Confirme la nueva contraseña')
        ],
        render_kw={
            'placeholder': 'Confirme la nueva contraseña',
            'class': 'form-control'
        }
    )
    
    submit = SubmitField(
        'Cambiar Contraseña',
        render_kw={
            'class': 'btn btn-primary'
        }
    )