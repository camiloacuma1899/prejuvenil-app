from flask_wtf import FlaskForm

from wtforms import (
    SelectField,
    StringField,
    IntegerField,
    DateField,
    SubmitField
)

from wtforms.validators import (
    DataRequired
)

from app.models.integrante import Integrante
from app.models.concepto_pago import ConceptoPago


class PagoForm(FlaskForm):

    integrante_id = SelectField(
        'Integrante',
        coerce=int,
        validators=[DataRequired()]
    )

    concepto = SelectField(
    'Concepto',
    coerce=int,
    validators=[DataRequired()]
)

    valor = IntegerField(
        'Valor',
        validators=[DataRequired()]
    )

    fecha = DateField(
        'Fecha',
        format='%Y-%m-%d',
        validators=[DataRequired()]
    )

    estado = SelectField(
        'Estado',
        choices=[
            ('Pendiente', 'Pendiente'),
            ('Abonado', 'Abonado'),
            ('Pagado', 'Pagado')
        ],
        validators=[DataRequired()]
    )

    observacion = StringField(
        'Observación'
    )

    submit = SubmitField(
        'Guardar Pago'
    )

    def cargar_integrantes(self):

        self.integrante_id.choices = [

            (i.id, i.nombre)

            for i in Integrante.query.order_by(
                Integrante.nombre
            ).all()

        ]

    def cargar_conceptos(self):

        self.concepto.coerce = int

        self.concepto.choices = [

        (c.id, c.nombre)

        for c in ConceptoPago.query.order_by(
            ConceptoPago.nombre
        ).all()

    ]