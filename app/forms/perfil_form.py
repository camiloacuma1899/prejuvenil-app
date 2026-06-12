from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    SubmitField
)

from wtforms.validators import (
    Optional,
    Email
)

from flask_wtf.file import (
    FileField,
    FileAllowed
)


class PerfilForm(FlaskForm):

    nombres = StringField(
        'Nombres'
    )

    apellidos = StringField(
        'Apellidos'
    )

    correo = StringField(
        'Correo',
        validators=[
            Optional(),
            Email()
        ]
    )

    telefono = StringField(
        'Teléfono'
    )

    foto = FileField(
        'Foto de perfil',
        validators=[
            FileAllowed(
                ['jpg', 'jpeg', 'png'],
                'Solo imágenes'
            )
        ]
    )

    submit = SubmitField(
        'Guardar Cambios'
    )