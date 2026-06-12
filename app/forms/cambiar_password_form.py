from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo


class CambiarPasswordForm(FlaskForm):

    password_actual = PasswordField(
        'Contraseña Actual',
        validators=[DataRequired()]
    )

    password_nueva = PasswordField(
        'Nueva Contraseña',
        validators=[DataRequired()]
    )

    confirmar_password = PasswordField(
        'Confirmar Contraseña',
        validators=[
            DataRequired(),
            EqualTo(
                'password_nueva',
                message='Las contraseñas no coinciden'
            )
        ]
    )

    submit = SubmitField(
        'Guardar Cambios'
    )