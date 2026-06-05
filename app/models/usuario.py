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

    def __repr__(self):

        return f'<Usuario {self.username}>'