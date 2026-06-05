from app import db


class Pago(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    integrante_id = db.Column(
        db.Integer,
        db.ForeignKey('integrante.id'),
        nullable=False
    )

    concepto = db.Column(
        db.String(150),
        nullable=False
    )

    valor = db.Column(
        db.Integer,
        nullable=False
    )

    fecha = db.Column(
        db.Date,
        nullable=False
    )

    estado = db.Column(
        db.String(50),
        nullable=False
    )

    observacion = db.Column(
        db.String(300)
    )

    def __repr__(self):

        return f'<Pago {self.concepto}>'