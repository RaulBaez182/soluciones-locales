from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    session
)

from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

import os
import uuid


app = Flask(__name__)

app.secret_key = "soluciones_locales"

app.config[
"SQLALCHEMY_DATABASE_URI"
] = "sqlite:///soluciones.db"

app.config[
"UPLOAD_FOLDER"
] = "static/uploads"

db = SQLAlchemy(app)


os.makedirs(
"static/uploads/perfiles",
exist_ok=True
)

os.makedirs(
"static/uploads/trabajos",
exist_ok=True
)


CIUDADES = [
"Asunción",
"Ciudad del Este",
"Encarnación",
"Luque",
"San Lorenzo",
"Capiatá"
]


OFICIOS = [

"Electricista",
"Plomero",
"Carpintero",
"Albañil",
"Pintor",
"Mecánico",
"Delivery",
"Diseñador Gráfico",
"Programador"

]


class Usuario(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nombre = db.Column(
        db.String(100)
    )

    apellido = db.Column(
        db.String(100)
    )

    email = db.Column(
        db.String(100),
        unique=True
    )

    password = db.Column(
        db.String(100)
    )

    telefono = db.Column(
        db.String(50)
    )

    ciudad = db.Column(
        db.String(100)
    )

    oficio = db.Column(
        db.String(100)
    )

    descripcion = db.Column(
        db.Text
    )

    perfil = db.Column(
        db.String(300)
    )

    img1 = db.Column(
        db.String(300)
    )

    img2 = db.Column(
        db.String(300)
    )

    img3 = db.Column(
        db.String(300)
    )

    estrellas = db.Column(
        db.Integer,
        default=5
    )

    favoritos = db.Column(
        db.Integer,
        default=0
    )


class Comentario(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    usuario_id = db.Column(
        db.Integer
    )

    texto = db.Column(
        db.Text
    )


with app.app_context():

    db.create_all()



def guardar(
archivo,
carpeta
):

    if (
        not archivo
        or
        archivo.filename == ""
    ):

        return ""


    nombre = (
        str(
            uuid.uuid4()
        )
        +
        "_"
        +
        secure_filename(
            archivo.filename
        )
    )

    ruta = os.path.join(
        app.config[
            "UPLOAD_FOLDER"
        ],
        carpeta,
        nombre
    )

    archivo.save(
        ruta
    )

    return "/" + ruta



@app.route("/")

def home():

    return render_template(
        "index.html"
    )



@app.route("/categorias")

def categorias():

    return jsonify(
        OFICIOS
    )



@app.route("/ciudades")

def ciudades():

    return jsonify(
        CIUDADES
    )



@app.route(
"/register",
methods=["POST"]
)

def register():

    data = request.form

    perfil = guardar(
        request.files.get(
            "perfil"
        ),
        "perfiles"
    )


    imgs = request.files.getlist(
        "trabajos"
    )


    lista = []


    for i in imgs[:3]:

        lista.append(
            guardar(
                i,
                "trabajos"
            )
        )


    while len(
        lista
    ) < 3:

        lista.append("")


    nuevo = Usuario(

        nombre=data[
            "nombre"
        ],

        apellido=data[
            "apellido"
        ],

        email=data[
            "email"
        ],

        password=data[
            "password"
        ],

        telefono=data[
            "telefono"
        ],

        ciudad=data[
            "ciudad"
        ],

        oficio=data[
            "oficio"
        ],

        descripcion=data[
            "descripcion"
        ],

        perfil=perfil,

        img1=lista[0],

        img2=lista[1],

        img3=lista[2]

    )


    db.session.add(
        nuevo
    )

    db.session.commit()


    return jsonify(
        {
            "ok":True
        }
    )



@app.route(
"/login",
methods=["POST"]
)

def login():

    email = request.form[
        "email"
    ]

    password = request.form[
        "password"
    ]


    u = Usuario.query.filter_by(

        email=email,
        password=password

    ).first()


    if not u:

        return jsonify(
            {
                "error":"credenciales"
            }
        )


    session[
        "user"
    ] = u.id


    return jsonify(
        {
            "ok":True
        }
    )



@app.route(
"/logout"
)

def logout():

    session.clear()

    return redirect(
        "/"
    )



@app.route(
"/buscar"
)

def buscar():

    ciudad = request.args.get(
        "ciudad"
    )

    oficio = request.args.get(
        "oficio"
    )

    q = Usuario.query


    if ciudad:

        q = q.filter_by(
            ciudad=ciudad
        )


    if oficio:

        q = q.filter_by(
            oficio=oficio
        )


    data = []


    for u in q.all():

        comentarios = Comentario.query.filter_by(
            usuario_id=u.id
        ).all()


        data.append({

            "id":
            u.id,

            "nombre":
            f"{u.nombre} {u.apellido}",

            "perfil":
            u.perfil,

            "oficio":
            u.oficio,

            "telefono":
            u.telefono,

            "descripcion":
            u.descripcion,

            "ciudad":
            u.ciudad,

            "favoritos":
            u.favoritos,

            "estrellas":
            u.estrellas,

            "imagenes":[
                u.img1,
                u.img2,
                u.img3
            ],

            "comentarios":[

                c.texto

                for c

                in comentarios

            ]

        })


    return jsonify(
        data
    )



@app.route(
"/favorito/<int:id>"
)

def favorito(id):

    u = Usuario.query.get(
        id
    )

    u.favoritos += 1

    db.session.commit()

    return jsonify(
        {
            "ok":True
        }
    )



@app.route(
"/comentario",
methods=["POST"]
)

def comentario():

    db.session.add(

        Comentario(

            usuario_id=
            request.form[
                "usuario"
            ],

            texto=
            request.form[
                "texto"
            ]

        )

    )

    db.session.commit()

    return jsonify(
        {
            "ok":True
        }
    )



@app.route(
"/eliminar/<int:id>"
)

def eliminar(id):

    u = Usuario.query.get(
        id
    )

    db.session.delete(
        u
    )

    db.session.commit()

    return redirect(
        "/"
    )



if __name__ == "__main__":

    app.run(
        debug=True
    )
