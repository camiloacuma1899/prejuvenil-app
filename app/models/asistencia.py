from app import db

class Asistencia(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    integrante_id = db.Column(
        db.Integer,
        db.ForeignKey('integrante.id'),
        nullable=False
    )

    encuentro_id = db.Column(
        db.Integer,
        db.ForeignKey('encuentro.id'),
        nullable=False
    )

    asistio = db.Column(
        db.Boolean,
        default=False
    )

    observacion = db.Column(
        db.String(300)
    )