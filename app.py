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

CIUDADES = ["Asunción","Ciudad del Este","Encarnación","Luque","San Lorenzo","Capiatá"]

OFICIOS = ["Electricista","Plomero","Albañil","Carpintero","Pintor","Herrero","Jardinero",
"Mecánico","Técnico de PCs","Diseñador Gráfico","Desarrollador Web","Fotógrafo",
"Chofer","Delivery","Profesor","Peluquero","Cocinero","Limpieza","Cerrajero"]

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    apellido = db.Column(db.String(100))
    email = db.Column(db.String(100))
    telefono = db.Column(db.String(100))
    ciudad = db.Column(db.String(100))
    oficio = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    perfil = db.Column(db.String(300))
    img1 = db.Column(db.String(300))
    img2 = db.Column(db.String(300))
    img3 = db.Column(db.String(300))

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/categorias")
def categorias():
    return jsonify(OFICIOS)

@app.route("/ciudades")
def ciudades():
    return jsonify(CIUDADES)

def save(file, folder):
    if not file:
        return ""
    name = secure_filename(file.filename)
    path = os.path.join(app.config["UPLOAD_FOLDER"], folder, name)
    file.save(path)
    return "/" + path

@app.route("/register", methods=["POST"])
def register():
    d = request.form

    perfil = save(request.files.get("perfil"), "perfiles")

    imgs = request.files.getlist("trabajos")
    gal = [save(i,"trabajos") for i in imgs[:3]]

    while len(gal)<3:
        gal.append("")

    u = Usuario(
        nombre=d["nombre"],
        apellido=d["apellido"],
        email=d["email"],
        telefono=d["telefono"],
        ciudad=d["ciudad"],
        oficio=d["oficio"],
        descripcion=d["descripcion"],
        perfil=perfil,
        img1=gal[0],
        img2=gal[1],
        img3=gal[2]
    )

    db.session.add(u)
    db.session.commit()

    return jsonify({"ok":True})

@app.route("/buscar")
def buscar():

    oficio = request.args.get("oficio","")
    ciudad = request.args.get("ciudad","")

    q = Usuario.query

    if oficio:
        q = q.filter_by(oficio=oficio)
    if ciudad:
        q = q.filter_by(ciudad=ciudad)

    data = q.all()

    return jsonify([
        {
            "id":u.id,
            "nombre":f"{u.nombre} {u.apellido}",
            "oficio":u.oficio,
            "ciudad":u.ciudad,
            "telefono":u.telefono,
            "descripcion":u.descripcion,
            "perfil":u.perfil,
            "imagenes":[u.img1,u.img2,u.img3],
            "rating":4.5
        }
        for u in data
    ])

if __name__ == "__main__":
    app.run(debug=True)
