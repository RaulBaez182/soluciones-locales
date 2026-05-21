from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///soluciones.db"
app.config["UPLOAD_FOLDER"] = "static/uploads"

db = SQLAlchemy(app)

os.makedirs("static/uploads/perfiles", exist_ok=True)
os.makedirs("static/uploads/trabajos", exist_ok=True)

# =========================
# MODELOS (Estructura profesional tipo Ñamba'apo)
# =========================

class Servicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    apellido = db.Column(db.String(100))
    telefono = db.Column(db.String(100))
    ciudad = db.Column(db.String(100))
    oficio = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    perfil = db.Column(db.String(300))
    img1 = db.Column(db.String(300))
    img2 = db.Column(db.String(300))
    img3 = db.Column(db.String(300))
     verificado = db.Column(db.Boolean, default=False) # Copiado de Ñamba'apo: Check de confianza

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicio.id'))
    nombre = db.Column(db.String(100))
    estrellas = db.Column(db.Integer) # 1 al 5
    comentario = db.Column(db.Text)

class Favorito(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    servicio_id = db.Column(db.Integer)
    user_key = db.Column(db.String(100))

with app.app_context():
    db.create_all()

# =========================
# LISTAS OFICIALES LOCALES
# =========================

@app.route("/categorias")
def categorias():
    lista_oficios = ["Plomero", "Electricista", "Carpintero", "Pintor", "Albañil", "Mecánico", "Fumigador", "Fleltero", "Cerrajero"]
    return jsonify(lista_oficios)

@app.route("/ciudades")
def ciudades():
    lista_ciudades = ["Asunción", "San Lorenzo", "Luque", "Lambaré", "Fernando de la Mora", "Capiatá", "Mariano Roque Alonso", "Ñemby"]
    return jsonify(lista_ciudades)

# =========================
# HOME
# =========================

@app.route("/")
def home():
    return render_template("index.html")

# =========================
# UPLOAD
# =========================

def save(file, folder):
    if not file or file.filename == '':
        return ""
    name = secure_filename(file.filename)
    path = os.path.join(app.config["UPLOAD_FOLDER"], folder, name)
    file.save(path)
    return "/" + path.replace("\\", "/")

# =========================
# REGISTRO
# =========================

@app.route("/register", methods=["POST"])
def register():
    d = request.form
    perfil = save(request.files.get("perfil"), "perfiles")
    imgs = request.files.getlist("trabajos")
    gal = [save(i,"trabajos") for i in imgs[:3]]

    while len(gal) < 3:
        gal.append("")

    s = Servicio(
        nombre=d["nombre"],
        apellido=d["apellido"],
        telefono=d["telefono"],
        ciudad=d["ciudad"],
        oficio=d["oficio"],
        descripcion=d["descripcion"],
        perfil=perfil,
        img1=gal[0],
        img2=gal[1],
        img3=gal[2],
        verificado=False
    )
    db.session.add(s)
    db.session.commit()
    return jsonify({"ok": True})

# =========================
# BUSCADOR CON RATING REAL (Idéntico a Ñamba'apo)
# =========================

@app.route("/buscar")
def buscar():
    oficio = request.args.get("oficio","")
    ciudad = request.args.get("ciudad","")

    q = Servicio.query
    if oficio:
        q = q.filter_by(oficio=oficio)
    if ciudad:
        q = q.filter_by(ciudad=ciudad)
    
    data = q.all()
    resultado = []

    for s in data:
        # Buscamos las reseñas reales de este trabajador en la base de datos
        reseñas = Review.query.filter_by(servicio_id=s.id).all()
        if reseñas:
            promedio_estrellas = round(sum(r.estrellas for r in reseñas) / len(reseñas), 1)
        else:
            promedio_estrellas = 0.0 # Sin calificaciones aún

        resultado.append({
            "id": s.id,
            "nombre": f"{s.nombre} {s.apellido}",
            "telefono": s.telefono,
            "ciudad": s.ciudad,
            "oficio": s.oficio,
            "descripcion": s.descripcion,
            "perfil": s.perfil,
            "imagenes": [s.img1, s.img2, s.img3],
            "verificado": s.verificado,
            "rating": promedio_estrellas if promedio_estrellas > 0 else "Nuevo"
        })

    return jsonify(resultado)

# =========================
# PERFIL DETALLADO + COMENTARIOS
# =========================

@app.route("/perfil/<int:id>")
def perfil(id):
    s = Servicio.query.get(id)
    if not s:
        return jsonify({"error":"no existe"})

    reseñas = Review.query.filter_by(servicio_id=s.id).all()
    promedio = round(sum(r.estrellas for r in reseñas) / len(reseñas), 1) if reseñas else 0.0

    return jsonify({
        "id": s.id,
        "nombre": f"{s.nombre} {s.apellido}",
        "telefono": s.telefono,
        "ciudad": s.ciudad,
        "oficio": s.oficio,
        "descripcion": s.descripcion,
        "perfil": s.perfil,
        "imagenes": [s.img1, s.img2, s.img3],
        "verificado": s.verificado,
        "rating": promedio,
        "comentarios": [{"usuario": r.nombre, "estrellas": r.estrellas, "texto": r.comentario} for r in reseñas]
    })

# =========================
# RESEÑAS Y FAVORITOS
# =========================

@app.route("/review", methods=["POST"])
def review():
    d = request.json
    r = Review(
        servicio_id=d["servicio_id"],
        nombre=d["nombre"],
        estrellas=int(d["estrellas"]),
        comentario=d["comentario"]
    )
    db.session.add(r)
    db.session.commit()
    return jsonify({"ok": True})

@app.route("/fav", methods=["POST"])
def fav():
    d = request.json
    f = Favorito(servicio_id=d["servicio_id"], user_key=d["user_key"])
    db.session.add(f)
    db.session.commit()
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True)
