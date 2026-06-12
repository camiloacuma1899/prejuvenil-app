from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    current_app,
    request,
    flash
)

from app import db

from flask_login import (

    login_user,

    logout_user,

    login_required,

    current_user

)

from werkzeug.security import (

    generate_password_hash,

    check_password_hash

)

from app.models.usuario import Usuario
from app.models.integrante import Integrante
from app.models.encuentro import Encuentro
from app.models.asistencia import Asistencia
from app.models.foto import Foto
from app.models.pago import Pago
from app.models.concepto_pago import ConceptoPago
from reportlab.lib.pagesizes import letter
from app.models.asistencia import Asistencia
from app.models.pago import Pago
from reportlab.lib.colors import HexColor
from reportlab.lib import colors
from app.forms.integrante_form import IntegranteForm
from app.forms.encuentro_form import EncuentroForm
from app.forms.importar_form import ImportarExcelForm
from app.forms.pago_form import PagoForm
from app.forms.foto_form import FotoForm
from app.utils.decorators import (
    roles_requeridos
)

import os
import pandas as pd
import cloudinary
import cloudinary.uploader

from datetime import date
from werkzeug.utils import secure_filename
from flask import send_file
from flask import jsonify
from reportlab.pdfgen import canvas

from io import BytesIO
main = Blueprint('main', __name__)


# =========================================
# INICIO
# =========================================

@main.route('/')
@login_required
def inicio():

    integrantes = Integrante.query.all()

    encuentros = Encuentro.query.all()

    fotos_recientes = Foto.query.order_by(
        Foto.fecha.desc()
    ).limit(6).all()

    return render_template(
        'index.html',
        integrantes=integrantes,
        encuentros=encuentros,
        fotos_recientes=fotos_recientes
    )


# =========================================
# DASHBOARD
# =========================================

@main.route('/dashboard')
@login_required
@roles_requeridos(
    'coordinador'
)
def dashboard():

    from datetime import date

    total_integrantes = Integrante.query.count()

    total_encuentros = Encuentro.query.count()

    total_asistencias = Asistencia.query.filter_by(
        asistio=True
    ).count()

    total_fallas = Asistencia.query.filter_by(
        asistio=False
    ).count()

    mes_actual = date.today().month

    cumpleaneros_mes = Integrante.query.filter(
        db.extract(
            'month',
            Integrante.fecha_nacimiento
        ) == mes_actual
    ).all()

    ranking_asistencia = db.session.query(

        Integrante.nombre,

        db.func.count(
            Asistencia.id
        ).label('total')

    ).join(

        Asistencia

    ).filter(

        Asistencia.asistio == True

    ).group_by(

        Integrante.nombre

    ).order_by(

        db.desc('total')

    ).limit(10).all()

    ranking_fallas = db.session.query(

        Integrante.nombre,

        db.func.count(
            Asistencia.id
        ).label('total')

    ).join(

        Asistencia

    ).filter(

        Asistencia.asistio == False

    ).group_by(

        Integrante.nombre

    ).order_by(

        db.desc('total')

    ).limit(10).all()
    # =========================================
    # ALERTAS DE AUSENCIA
    # =========================================

    integrantes_alerta = []

    integrantes = Integrante.query.all()

    for integrante in integrantes:

        total_fallas_integrante = Asistencia.query.filter_by(
            integrante_id=integrante.id,
            asistio=False
        ).count()

        if total_fallas_integrante >= 3:

            integrantes_alerta.append({

                'nombre': integrante.nombre,

                'fallas': total_fallas_integrante

            })
    return render_template(

        'dashboard.html',

        total_integrantes=total_integrantes,

        total_encuentros=total_encuentros,

        total_asistencias=total_asistencias,

        total_fallas=total_fallas,

        cumpleaneros_mes=cumpleaneros_mes,

        ranking_asistencia=ranking_asistencia,

        ranking_fallas=ranking_fallas,

        integrantes_alerta=integrantes_alerta

    )

# =========================================
# IMPORTAR EXCEL
# =========================================

@main.route('/importar', methods=['GET', 'POST'])
def importar_excel():

    form = ImportarExcelForm()

    if form.validate_on_submit():

        archivo = form.archivo.data

        nombre_archivo = secure_filename(
            archivo.filename
        )

        ruta = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            nombre_archivo
        )

        archivo.save(ruta)

        df = pd.read_excel(ruta)

        for _, fila in df.iterrows():

            try:

                integrante = Integrante(

                    nombre=str(
                        fila.get('nombre', '')
                    ),

                    fecha_nacimiento=fila.get(
                        'fecha_nacimiento'
                    ),

                    edad=int(
                        fila.get('edad', 0)
                    ),

                    telefono=str(
                        fila.get('telefono', '')
                    ),

                    alergia=str(
                        fila.get('alergia', '')
                    ),

                    acudiente=str(
                        fila.get('acudiente', '')
                    ),

                    nombre_acudiente=str(
                        fila.get(
                            'nombre_acudiente',
                            ''
                        )
                    ),

                    telefono_acudiente=str(
                        fila.get(
                            'telefono_acudiente',
                            ''
                        )
                    )

                )

                db.session.add(integrante)

            except Exception as e:

                print(e)

        db.session.commit()

        flash(
            'Excel importado correctamente'
        )

        return redirect(
            url_for('main.inicio')
        )

    return render_template(
        'importar_excel.html',
        form=form
    )


# =========================================
# NUEVO INTEGRANTE
# =========================================

@main.route('/nuevo', methods=['GET', 'POST'])
@main.route('/nuevo', methods=['GET', 'POST'])
@login_required
@roles_requeridos(
    'coordinador'
)
def nuevo_integrante():

    form = IntegranteForm()

    if form.validate_on_submit():

        nombre_foto = None

    foto = form.foto.data

    if foto and foto.filename != '':

        resultado = cloudinary.uploader.upload(
        foto,
        folder="integrantes"
    )

        nombre_foto = resultado["secure_url"]

        hoy = date.today()

        edad_calculada = (
            hoy.year
            - form.fecha_nacimiento.data.year
            - (
                (hoy.month, hoy.day)
                <
                (
                    form.fecha_nacimiento.data.month,
                    form.fecha_nacimiento.data.day
                )
            )
        )

        integrante = Integrante(

            nombre=form.nombre.data,

            fecha_nacimiento=form.fecha_nacimiento.data,

            edad=edad_calculada,

            telefono=form.telefono.data,

            alergia=form.alergia.data,

            acudiente=form.acudiente.data,

            nombre_acudiente=form.nombre_acudiente.data,

            telefono_acudiente=form.telefono_acudiente.data,

            foto=nombre_foto

        )

        db.session.add(integrante)

        db.session.commit()

        return redirect(
            url_for('main.inicio')
        )

    return render_template(
        'nuevo_integrante.html',
        form=form
    )

# =========================================
# EDITAR INTEGRANTE
# =========================================

@main.route('/editar/<int:id>', methods=['GET', 'POST'])
@main.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_requeridos(
    'coordinador'
)
def editar_integrante(id):

    integrante = Integrante.query.get_or_404(id)

    form = IntegranteForm(obj=integrante)

    if form.validate_on_submit():

        integrante.nombre = form.nombre.data
        integrante.fecha_nacimiento = form.fecha_nacimiento.data

        hoy = date.today()

        integrante.edad = (
            hoy.year
            - form.fecha_nacimiento.data.year
            - (
                (hoy.month, hoy.day)
                <
                (
                    form.fecha_nacimiento.data.month,
                    form.fecha_nacimiento.data.day
                )
            )
        )

        integrante.telefono = form.telefono.data
        integrante.alergia = form.alergia.data
        integrante.acudiente = form.acudiente.data
        integrante.nombre_acudiente = form.nombre_acudiente.data
        integrante.telefono_acudiente = form.telefono_acudiente.data

        foto = form.foto.data

        print("FOTO RECIBIDA:", foto)

        if foto and foto.filename != '':

            resultado = cloudinary.uploader.upload(
                foto,
                folder="integrantes"
            )

            print("RESULTADO CLOUDINARY:")
            print(resultado)

            integrante.foto = resultado["secure_url"]

            print("URL GUARDADA:")
            print(integrante.foto)

        db.session.commit()

        print("COMMIT REALIZADO")

        return redirect(
            url_for('main.inicio')
        )

    return render_template(
        'nuevo_integrante.html',
        form=form
    )
# =========================================
# VER INTENGRANTE
# =========================================

@main.route('/integrante/<int:id>')
def ver_integrante(id):

    integrante = Integrante.query.get_or_404(id)

    return render_template(
        'ver_integrante.html',
        integrante=integrante
    )

# =========================================
# ELIMINAR INTEGRANTE
# =========================================

@main.route('/eliminar/<int:id>')
@login_required
@roles_requeridos('coordinador')
def eliminar_integrante(id):

    integrante = Integrante.query.get_or_404(id)

    # ELIMINAR ASISTENCIAS

    Asistencia.query.filter_by(
        integrante_id=integrante.id
    ).delete()

    # ELIMINAR PAGOS

    Pago.query.filter_by(
        integrante_id=integrante.id
    ).delete()

    # ELIMINAR INTEGRANTE

    db.session.delete(integrante)

    db.session.commit()

    return redirect(
        url_for('main.inicio')
    )

# =========================================
# ENCUENTROS
# =========================================

@main.route('/encuentros')
@login_required
@roles_requeridos(
    'coordinador',
    'joven'
)
def encuentros():

    encuentros = Encuentro.query.all()

    return render_template(
        'encuentros.html',
        encuentros=encuentros
    )


@main.route('/encuentros/nuevo', methods=['GET', 'POST'])
@login_required
@roles_requeridos(
    'coordinador'
)
def nuevo_encuentro():

    form = EncuentroForm()

    if form.validate_on_submit():

        encuentro = Encuentro(

    titulo=form.titulo.data,

    fecha=form.fecha.data,

    tema=form.tema.data,

    observaciones=form.observaciones.data,

    notas_privadas=form.notas_privadas.data

)

        db.session.add(encuentro)

        db.session.commit()

        return redirect(
            url_for('main.encuentros')
        )

    return render_template(
        'nuevo_encuentro.html',
        form=form
    )


# =========================================
# ASISTENCIA
# =========================================

@main.route('/asistencia/<int:encuentro_id>', methods=['GET', 'POST'])
@login_required
@roles_requeridos(
    'coordinador',
    'joven'
)
def asistencia(encuentro_id):

    encuentro = Encuentro.query.get_or_404(
        encuentro_id
    )

    integrantes = Integrante.query.order_by(
        Integrante.nombre
    ).all()

    # CARGAR ASISTENCIAS EXISTENTES
    asistencias_existentes = {}

    asistencias_db = Asistencia.query.filter_by(
        encuentro_id=encuentro_id
    ).all()

    for asistencia in asistencias_db:

        asistencias_existentes[
            asistencia.integrante_id
        ] = asistencia

    # GUARDAR / ACTUALIZAR
    if request.method == 'POST' and current_user.rol == 'coordinador':

        for integrante in integrantes:

            asistio = request.form.get(
                f'asistencia_{integrante.id}'
            ) == 'on'

            observacion = request.form.get(
                f'observacion_{integrante.id}'
            )

            asistencia_existente = Asistencia.query.filter_by(

                integrante_id=integrante.id,

                encuentro_id=encuentro_id

            ).first()

            # ACTUALIZAR
            if asistencia_existente:

                asistencia_existente.asistio = asistio

                asistencia_existente.observacion = observacion
            
            # CREAR
            else:

                nueva_asistencia = Asistencia(

                    integrante_id=integrante.id,

                    encuentro_id=encuentro_id,

                    asistio=asistio,

                    observacion=observacion

                )

                db.session.add(
                    nueva_asistencia
                )

        db.session.commit()

        flash(
            'Asistencia guardada correctamente'
        )

        return redirect(

            url_for(
                'main.asistencia',
                encuentro_id=encuentro_id
            )

        )

    return render_template(

        'asistencia.html',

        encuentro=encuentro,

        integrantes=integrantes,

        asistencias_existentes=asistencias_existentes

    )
@main.route('/integrante/<int:id>/pdf')
def generar_pdf(id):

    integrante = Integrante.query.get_or_404(id)

    buffer = BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=letter
    )

    width, height = letter

    # =========================
    # COLORES
    # =========================

    azul = HexColor("#2563eb")

    gris = HexColor("#64748b")

    negro = HexColor("#0f172a")

    fondo = HexColor("#f8fafc")

    # =========================
    # FONDO
    # =========================

    pdf.setFillColor(fondo)

    pdf.rect(
        0,
        0,
        width,
        height,
        fill=1,
        stroke=0
    )

    # =========================
    # HEADER
    # =========================

    pdf.setFillColor(azul)

    pdf.roundRect(
        40,
        720,
        530,
        90,
        20,
        fill=1,
        stroke=0
    )

    pdf.setFillColor(colors.white)

    pdf.setFont(
        "Helvetica-Bold",
        24
    )

    pdf.drawString(
        60,
        775,
        "Ficha del Integrante"
    )

    pdf.setFont(
        "Helvetica",
        13
    )

    pdf.drawString(
        60,
        748,
        "Grupo Prejuvenil San Carlo Acutis"
    )

    # =========================
    # FOTO
    # =========================

    foto_path = None

    if integrante.foto:

        foto_path = os.path.join(
            current_app.static_folder,
            'uploads',
            integrante.foto
        )

    if foto_path and os.path.exists(foto_path):

        pdf.drawImage(

            foto_path,

            60,
            540,

            width=120,

            height=140,

            preserveAspectRatio=True,

            mask='auto'

        )

    else:

        pdf.setFillColor(HexColor("#e2e8f0"))

        pdf.roundRect(
            60,
            540,
            120,
            140,
            16,
            fill=1,
            stroke=0
        )

        pdf.setFillColor(gris)

        pdf.setFont(
            "Helvetica-Bold",
            40
        )

        pdf.drawCentredString(
            120,
            600,
            "👤"
        )

    # =========================
    # NOMBRE
    # =========================

    pdf.setFillColor(negro)

    pdf.setFont(
        "Helvetica-Bold",
        22
    )

    pdf.drawString(
        210,
        650,
        integrante.nombre
    )

    pdf.setFillColor(gris)

    pdf.setFont(
        "Helvetica",
        12
    )

    pdf.drawString(
        210,
        625,
        f"Edad: {integrante.edad_calculada} años"
    )

    pdf.drawString(
        210,
        605,
        f"Teléfono: {integrante.telefono}"
    )

    # =========================
    # INFO PERSONAL
    # =========================

    pdf.setFillColor(colors.white)

    pdf.roundRect(
        40,
        410,
        530,
        100,
        18,
        fill=1,
        stroke=0
    )

    pdf.setFillColor(azul)

    pdf.setFont(
        "Helvetica-Bold",
        15
    )

    pdf.drawString(
        60,
        485,
        "Información Personal"
    )

    pdf.setFillColor(negro)

    pdf.setFont(
        "Helvetica",
        12
    )

    pdf.drawString(
        60,
        455,
        f"Fecha de nacimiento: {integrante.fecha_nacimiento}"
    )

    pdf.drawString(
        60,
        430,
        f"Alergias: {integrante.alergia or 'Sin registro'}"
    )

    # =========================
    # ACUDIENTE
    # =========================

    pdf.setFillColor(colors.white)

    pdf.roundRect(
        40,
        280,
        530,
        100,
        18,
        fill=1,
        stroke=0
    )

    pdf.setFillColor(azul)

    pdf.setFont(
        "Helvetica-Bold",
        15
    )

    pdf.drawString(
        60,
        355,
        "Información del Acudiente"
    )

    pdf.setFillColor(negro)

    pdf.setFont(
        "Helvetica",
        12
    )

    pdf.drawString(
        60,
        325,
        f"Relación: {integrante.acudiente}"
    )

    pdf.drawString(
        60,
        300,
        f"Nombre: {integrante.nombre_acudiente}"
    )

    pdf.drawString(
        320,
        300,
        f"Teléfono: {integrante.telefono_acudiente}"
    )

    # =========================
    # FOOTER
    # =========================

    pdf.setFillColor(gris)

    pdf.setFont(
        "Helvetica-Oblique",
        10
    )

    pdf.drawString(
        40,
        40,
        "Documento generado automáticamente por el sistema."
    )

    pdf.save()

    buffer.seek(0)

    return send_file(

        buffer,

        as_attachment=True,

        download_name=f"{integrante.nombre}.pdf",

        mimetype='application/pdf'

    )
# =========================================
# GALERIA
# =========================================

@main.route('/galeria')
def galeria():

    fotos = Foto.query.order_by(
        Foto.fecha.desc()
    ).all()

    return render_template(
        'galeria.html',
        fotos=fotos
    )


@main.route(
    '/galeria/subir',
    methods=['GET', 'POST']
)
@login_required
@roles_requeridos(
    'coordinador'
)


def subir_foto():

    form = FotoForm()

    if form.validate_on_submit():

        archivo = form.archivo.data

        resultado = cloudinary.uploader.upload(
            archivo,
            folder="galeria"
        )

        foto = Foto(
            titulo=form.titulo.data,
            archivo=resultado["secure_url"]
        )

        db.session.add(foto)
        db.session.commit()

        return redirect(
            url_for('main.galeria')
        )

    return render_template(
        'subir_foto.html',
        form=form
    )
def ver_foto(id):

    foto = Foto.query.get_or_404(id)

    return render_template(
        'ver_foto.html',
        foto=foto
    )

@main.route('/foto/eliminar/<int:id>')
@login_required
@roles_requeridos(
    'coordinador'
)
@main.route('/foto/eliminar/<int:id>')
@login_required
@roles_requeridos('coordinador')
def eliminar_foto(id):

    foto = Foto.query.get_or_404(id)

    db.session.delete(foto)

    db.session.commit()

    flash(
        'Foto eliminada correctamente'
    )

    return redirect(
        url_for('main.galeria')
    )

def nuevo_pago():

    form = PagoForm()

    form.cargar_integrantes()
    form.cargar_conceptos()

    if form.validate_on_submit():

        pago = Pago(
            integrante_id=form.integrante_id.data,
            concepto = ConceptoPago.query.get(
            form.concepto.data
            ).nombre,
            valor=form.valor.data,
            fecha=form.fecha.data,
            estado=form.estado.data,
            observacion=form.observacion.data
        )

        db.session.add(pago)
        db.session.commit()

        flash(
            'Pago registrado correctamente'
        )

        return redirect(
            url_for('main.lista_pagos')
        )

    return render_template(
        'nuevo_pago.html',
        form=form
    )

@main.route('/pagos')
@login_required
@roles_requeridos(
    'coordinador'
)
def lista_pagos():

    pagos = Pago.query.order_by(
        Pago.fecha.desc()
    ).all()

    return render_template(
        'pagos.html',
        pagos=pagos
    )

@main.route('/estado-cuenta/<int:id>')
@login_required
@roles_requeridos(
    'coordinador'
)
def estado_cuenta(id):

    integrante = Integrante.query.get_or_404(id)

    pagos = Pago.query.filter_by(
        integrante_id=id
    ).all()

    conceptos = ConceptoPago.query.all()

    total_pagado = sum(
        pago.valor
        for pago in pagos
        if pago.estado == 'Pagado'
    )

    total_abonado = sum(
        pago.valor
        for pago in pagos
        if pago.estado == 'Abonado'
    )

    total_conceptos = sum(
        concepto.valor
        for concepto in conceptos
    )

    saldo_pendiente = (
        total_conceptos
        - total_pagado
        - total_abonado
    )

    if saldo_pendiente < 0:
        saldo_pendiente = 0

    return render_template(

        'estado_cuenta.html',

        integrante=integrante,

        pagos=pagos,

        total_pagado=total_pagado,

        total_abonado=total_abonado,

        total_conceptos=total_conceptos,

        saldo_pendiente=saldo_pendiente

    )

@main.route('/conceptos')
@login_required
@roles_requeridos(
    'coordinador'
)
def conceptos():

    conceptos = ConceptoPago.query.order_by(
        ConceptoPago.nombre
    ).all()

    return render_template(
        'conceptos.html',
        conceptos=conceptos
    )

@main.route('/conceptos/nuevo', methods=['GET', 'POST'])
@login_required
@roles_requeridos(
    'coordinador'
)
def nuevo_concepto():

    if request.method == 'POST':

        nombre = request.form.get(
            'nombre'
        )

        valor = request.form.get(
            'valor'
        )

        concepto = ConceptoPago(

            nombre=nombre,

            valor=int(valor)

        )

        db.session.add(concepto)

        db.session.commit()

        flash(
            'Concepto creado correctamente'
        )

        return redirect(
            url_for('main.conceptos')
        )

    return render_template(
        'nuevo_concepto.html'
    )

@main.route('/concepto/<int:id>')
def obtener_concepto(id):

    concepto = ConceptoPago.query.get_or_404(id)

    return jsonify({

        'id': concepto.id,

        'nombre': concepto.nombre,

        'valor': concepto.valor

    })

@main.route('/encuentro/<int:id>')
@login_required
@roles_requeridos(
    'coordinador',
    'joven'

)
def ver_encuentro(id):

    encuentro = Encuentro.query.get_or_404(id)

    asistencias = Asistencia.query.filter_by(
        encuentro_id=id
    ).all()

    total_asistieron = len([

        a for a in asistencias
        if a.asistio

    ])

    total_faltaron = len([

        a for a in asistencias
        if not a.asistio

    ])

    return render_template(

        'ver_encuentro.html',

        encuentro=encuentro,

        asistencias=asistencias,

        total_asistieron=total_asistieron,

        total_faltaron=total_faltaron

    )

@main.route('/encuentro/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_requeridos(
    'coordinador'
)
def editar_encuentro(id):

    encuentro = Encuentro.query.get_or_404(id)

    form = EncuentroForm(
        obj=encuentro
    )

    if form.validate_on_submit():

        encuentro.titulo = form.titulo.data

        encuentro.fecha = form.fecha.data

        encuentro.tema = form.tema.data

        encuentro.observaciones = form.observaciones.data

        encuentro.notas_privadas = form.notas_privadas.data

        db.session.commit()

        flash(
            'Encuentro actualizado correctamente'
        )

        return redirect(

            url_for(
                'main.ver_encuentro',
                id=encuentro.id
            )

        )

    return render_template(

        'nuevo_encuentro.html',

        form=form,

        editar=True

    )

@main.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form.get(
            'username'
        )

        password = request.form.get(
            'password'
        )

        usuario = Usuario.query.filter_by(
            username=username
        ).first()

        if usuario and check_password_hash(

            usuario.password,

            password

        ):

            login_user(usuario)

            return redirect(
                url_for('main.inicio')
            )

        flash(
            'Usuario o contraseña incorrectos'
        )

    return render_template(
        'login.html'
    )

@main.route('/logout')
@login_required
def logout():

    logout_user()

    flash(
        'Sesión cerrada'
    )

    return redirect(
        url_for('main.login')
    )

@main.route('/crear-admin')
def crear_admin():

    existe = Usuario.query.filter_by(
        username='admin'
    ).first()

    if existe:

        return 'El usuario admin ya existe'

    admin = Usuario(

        username='admin',

        password=generate_password_hash(
            '123456'
        ),

        rol='coordinador'

    )

    db.session.add(admin)

    db.session.commit()


    return 'Administrador creado'

@main.route('/usuarios')
@login_required
@roles_requeridos(
    'coordinador'
)
def usuarios():

    usuarios = Usuario.query.order_by(
        Usuario.username
    ).all()

    return render_template(

        'usuarios.html',

        usuarios=usuarios

    )

@main.route('/usuarios/nuevo', methods=['GET', 'POST'])
@login_required
@roles_requeridos(
    'coordinador'
)
def nuevo_usuario():

    if request.method == 'POST':

        username = request.form.get(
            'username'
        )

        password = request.form.get(
            'password'
        )

        rol = request.form.get(
            'rol'
        )

        existe = Usuario.query.filter_by(
            username=username
        ).first()

        if existe:

            flash(
                'El usuario ya existe'
            )

            return redirect(
                url_for('main.nuevo_usuario')
            )

        usuario = Usuario(

            username=username,

            password=generate_password_hash(
                password
            ),

            rol=rol

        )

        db.session.add(usuario)

        db.session.commit()

        flash(
            'Usuario creado correctamente'
        )

        return redirect(
            url_for('main.usuarios')
        )

    return render_template(
        'nuevo_usuario.html'
    )
