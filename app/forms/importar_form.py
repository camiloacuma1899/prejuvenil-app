from flask_wtf import FlaskForm

from flask_wtf.file import FileField

from wtforms import SubmitField

from wtforms.validators import DataRequired


class ImportarExcelForm(FlaskForm):

    archivo = FileField(

        'Archivo Excel',

        validators=[
            DataRequired()
        ]

    )

    submit = SubmitField(
        'Importar Excel'
    )