from app import db
from datetime import date


class Integrante(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(150),
        nullable=False
    )

    fecha_nacimiento = db.Column(
        db.Date,
        nullable=False
    )

    edad = db.Column(
        db.Integer,
        nullable=False
    )

    telefono = db.Column(
        db.String(20),
        nullable=False
    )

    alergia = db.Column(
        db.String(200)
    )

    acudiente = db.Column(
        db.String(150),
        nullable=False
    )

    nombre_acudiente = db.Column(
        db.String(150),
        nullable=False
    )

    telefono_acudiente = db.Column(
        db.String(20),
        nullable=False
    )

    foto = db.Column(
        db.String(200)
    )

    asistencias = db.relationship(
        'Asistencia',
        backref='integrante',
        lazy=True
    )

    pagos = db.relationship(
        'Pago',
        backref='integrante',
        lazy=True
    )

    @property
    def edad_calculada(self):

        if not self.fecha_nacimiento:
            return 0

        hoy = date.today()

        return (
            hoy.year
            - self.fecha_nacimiento.year
            - (
                (hoy.month, hoy.day)
                <
                (
                    self.fecha_nacimiento.month,
                    self.fecha_nacimiento.day
                )
            )
        )

    def __repr__(self):

        return f'<Integrante {self.nombre}>'