from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    SubmitField,
    FileField
)

from wtforms.validators import (
    DataRequired
)


class FotoForm(FlaskForm):

    titulo = StringField(

        'Título',

        validators=[
            DataRequired()
        ]

    )

    archivo = FileField(

        'Fotografía',

        validators=[
            DataRequired()
        ]

    )

    submit = SubmitField(
        'Subir Foto'
    )