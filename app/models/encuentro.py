from app import db

class Encuentro(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    titulo = db.Column(
        db.String(150),
        nullable=False
    )

    fecha = db.Column(
        db.Date,
        nullable=False
    )

    tema = db.Column(
        db.String(300)
    )

    observaciones = db.Column(
        db.Text
    )

    notas_privadas = db.Column(
    db.Text
)

    asistencias = db.relationship(
        'Asistencia',
        backref='encuentro',
        lazy=True
    )

    def __repr__(self):

        return f'<Encuentro {self.titulo}>'