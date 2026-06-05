from functools import wraps

from flask_login import current_user

from flask import redirect
from flask import url_for
from flask import flash


def roles_requeridos(*roles):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            if current_user.rol not in roles:

                flash(
                    'No tienes permiso para acceder'
                )

                return redirect(
                    url_for('main.inicio')
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator