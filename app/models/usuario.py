from app import db

from flask_login import UserMixin


class Usuario(

    db.Model,

    UserMixin

):

    id = db.Column(

        db.Integer,

        primary_key=True

    )

    username = db.Column(

        db.String(100),

        unique=True,

        nullable=False

    )

    password = db.Column(

        db.String(300),

        nullable=False

    )

    rol = db.Column(

        db.String(50),

        nullable=False

    )

    nombres = db.Column(

        db.String(150)

    )

    apellidos = db.Column(

        db.String(150)

    )

    correo = db.Column(

        db.String(150)

    )

    telefono = db.Column(

        db.String(30)

    )

    foto = db.Column(

        db.String(500)

    )

    fecha_creacion = db.Column(

        db.DateTime,

        default=db.func.now()

    )

    def nombre_completo(self):

        nombres = self.nombres or ''

        apellidos = self.apellidos or ''

        return f"{nombres} {apellidos}".strip()

    def __repr__(self):

        return f'<Usuario {self.username}>'