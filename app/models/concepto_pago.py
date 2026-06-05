from app import db


class ConceptoPago(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(150),
        nullable=False
    )

    valor = db.Column(
        db.Integer,
        nullable=False
    )

    activo = db.Column(
        db.Boolean,
        default=True
    )

    def __repr__(self):

        return f'<ConceptoPago {self.nombre}>'