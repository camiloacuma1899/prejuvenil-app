from app import db


class Foto(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    titulo = db.Column(
        db.String(200),
        nullable=False
    )

    archivo = db.Column(
        db.String(255),
        nullable=False
    )

    fecha = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    def __repr__(self):

        return f'<Foto {self.titulo}>'