from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    DateField,
    TextAreaField,
    SubmitField
)

from wtforms.validators import (
    DataRequired
)


class EncuentroForm(FlaskForm):

    titulo = StringField(

        'Título',

        validators=[
            DataRequired()
        ]

    )

    fecha = DateField(

        'Fecha',

        validators=[
            DataRequired()
        ]

    )

    tema = StringField(

        'Tema'

    )

    observaciones = TextAreaField(

        'Observaciones Públicas'

    )

    notas_privadas = TextAreaField(

        'Notas Privadas de Coordinación'

    )

    submit = SubmitField(

        'Guardar'

    )