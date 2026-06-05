from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    DateField,
    SubmitField,
    FileField
)

from wtforms.validators import (
    DataRequired,
    Length
)


class IntegranteForm(FlaskForm):

    nombre = StringField(

        'Nombre',

        validators=[

            DataRequired(
                message='El nombre es obligatorio'
            ),

            Length(
                min=3,
                max=150
            )

        ]

    )

    fecha_nacimiento = DateField(

        'Fecha de Nacimiento',

        validators=[

            DataRequired(
                message='La fecha es obligatoria'
            )

        ]

    )

    telefono = StringField(

        'Teléfono',

        validators=[

            DataRequired(
                message='El teléfono es obligatorio'
            )

        ]

    )

    alergia = StringField(
        'Alergia'
    )

    acudiente = StringField(

        'Acudiente',

        validators=[

            DataRequired(
                message='El acudiente es obligatorio'
            )

        ]

    )

    nombre_acudiente = StringField(

        'Nombre Acudiente',

        validators=[

            DataRequired(
                message='El nombre del acudiente es obligatorio'
            )

        ]

    )

    telefono_acudiente = StringField(

        'Teléfono Acudiente',

        validators=[

            DataRequired(
                message='El teléfono del acudiente es obligatorio'
            )

        ]

    )

    foto = FileField(
        'Foto'
    )

    submit = SubmitField(
        'Guardar'
    )