from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'db.sqlite')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Servicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    apellido = db.Column(db.String(100))
    telefono = db.Column(db.String(50))
    ciudad = db.Column(db.String(100))
    oficio = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    perfil_url = db.Column(db.String(300))

with app.app_context():
    db.create_all()

    if Servicio.query.count() == 0:
        db.session.add_all([
            Servicio(nombre="Juan", apellido="Perez", telefono="123", ciudad="Asunción", oficio="Plomero", descripcion="Experto", perfil_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d"),
            Servicio(nombre="Ana", apellido="Lopez", telefono="456", ciudad="Luque", oficio="Electricista", descripcion="Instalaciones", perfil_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330")
        ])
        db.session.commit()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    data = request.json

    s = Servicio(
        nombre=data.get("nombre"),
        apellido=data.get("apellido"),
        telefono=data.get("telefono"),
        ciudad=data.get("ciudad"),
        oficio=data.get("oficio"),
        descripcion=data.get("descripcion"),
        perfil_url="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde"
    )

    db.session.add(s)
    db.session.commit()

    return jsonify({"ok": True})

@app.route("/buscar")
def buscar():
    oficio = request.args.get("oficio")

    q = Servicio.query
    if oficio:
        q = q.filter(Servicio.oficio.like(f"%{oficio}%"))

    return jsonify([
        {
            "id": s.id,
            "nombre": s.nombre + " " + s.apellido,
            "telefono": s.telefono,
            "ciudad": s.ciudad,
            "oficio": s.oficio,
            "descripcion": s.descripcion,
            "perfil_url": s.perfil_url
        }
        for s in q.all()
    ])

@app.route("/perfil/<int:id>")
def perfil(id):
    s = Servicio.query.get(id)
    if not s:
        return jsonify({"error": "no existe"})
    return jsonify({
        "nombre": s.nombre + " " + s.apellido,
        "telefono": s.telefono,
        "ciudad": s.ciudad,
        "oficio": s.oficio,
        "descripcion": s.descripcion,
        "perfil_url": s.perfil_url
    })

if __name__ == "__main__":
    app.run()
