from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate

from flask_login import LoginManager


db = SQLAlchemy()

migrate = Migrate()

login_manager = LoginManager()

login_manager.login_view = 'main.login'
login_manager.login_message = 'Debes iniciar sesión'

login_manager.login_message_category = 'warning'

def create_app():

    import os


    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'san-carlo-acutis'

    database_url = os.getenv('DATABASE_URL')

    if database_url:

        database_url = database_url.replace(
        "postgres://",
        "postgresql://",
        1
    )

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['UPLOAD_FOLDER'] = 'app/static/uploads'

    app.config['WTF_CSRF_ENABLED'] = False

    db.init_app(app)

    migrate.init_app(app, db)

    login_manager.init_app(app)

    from app.models.integrante import Integrante

    from app.models.encuentro import Encuentro

    from app.models.asistencia import Asistencia

    from app.models.pago import Pago

    from app.models.concepto_pago import ConceptoPago

    from app.models.usuario import Usuario

    from app.routes.routes import main

    app.register_blueprint(main)

    with app.app_context():

        db.create_all()

    from app.models.usuario import Usuario

    from werkzeug.security import generate_password_hash

    admin = Usuario.query.filter_by(
        username='admin'
    ).first()

    if not admin:

        nuevo_admin = Usuario(
            username='admin',
            password=generate_password_hash('1234'),
            rol='coordinador'
        )

        db.session.add(nuevo_admin)

        db.session.commit()


    return app


@login_manager.user_loader
def load_user(user_id):

    from app.models.usuario import Usuario

    return Usuario.query.get(
        int(user_id)
    )
    