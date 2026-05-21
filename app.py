from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Configuración de Base de Datos local automática
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'soluciones.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# =========================
# MODELOS DE BASE DE DATOS
# =========================
class Servicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    apellido = db.Column(db.String(100))
    telefono = db.Column(db.String(100))
    ciudad = db.Column(db.String(100))
    oficio = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    perfil_url = db.Column(db.String(300)) # Foto por defecto

with app.app_context():
    db.create_all()
    # Inyecta datos automáticamente para que la app no aparezca vacía la primera vez
    if Servicio.query.count() == 0:
        base_profesionales = [
            Servicio(nombre="Juan Ramón", apellido="Pérez", telefono="0981123456", ciudad="Asunción", oficio="Plomero", descripcion="Especialista en cañerías, termocalefones, canillas y filtraciones en general. Atención rápida en Asunción y alrededores.", perfil_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150"),
            Servicio(nombre="Lizza Andrea", apellido="Verón", telefono="0971987654", ciudad="San Lorenzo", oficio="Electricista", descripcion="Instalaciones eléctricas residenciales. Cableados nuevos, cortocircuitos, instalación de duchas y tableros.", perfil_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150"),
            Servicio(nombre="Samuel", apellido="Valdez", telefono="0961112233", ciudad="Luque", oficio="Carpintero", descripcion="Trabajos de carpintería fina, reparación de puertas, muebles de cocina a medida y restauración.", perfil_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150")
        ]
        db.session.bulk_save_objects(base_profesionales)
        db.session.commit()

# =========================
# RUTAS DE LA APP
# =========================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    d = request.json # Recibe el JSON limpio del formulario móvil
    nuevo_servicio = Servicio(
        nombre=d.get("nombre", ""),
        apellido=d.get("apellido", ""),
        telefono=d.get("telefono", ""),
        ciudad=d.get("ciudad", "Asunción"),
        oficio=d.get("oficio", "Plomero"),
        descripcion=d.get("descripcion", ""),
        perfil_url="https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150" # Foto gris estándar de perfil
    )
    db.session.add(nuevo_servicio)
    db.session.commit()
    return jsonify({"ok": True})

@app.route("/buscar")
def buscar():
    oficio = request.args.get("oficio", "")
    ciudad = request.args.get("ciudad", "")

    q = Servicio.query
    if oficio:
        q = q.filter(Servicio.oficio.like(f"%{oficio}%"))
    if ciudad:
        q = q.filter(Servicio.ciudad.like(f"%{ciudad}%"))
    
    data = q.all()
    resultado = []
    for s in data:
        resultado.append({
            "id": s.id,
            "nombre": f"{s.nombre} {s.apellido}",
            "telefono": s.telefono,
            "ciudad": s.ciudad,
            "oficio": s.oficio,
            "descripcion": s.descripcion,
            "perfil_url": s.perfil_url
        })
    return jsonify(resultado)

@app.route("/perfil/<int:id>")
def perfil(id):
    s = Servicio.query.get(id)
    if not s:
        return jsonify({"error": "no existe"}), 404
    return jsonify({
        "id": s.id,
        "nombre": f"{s.nombre} {s.apellido}",
        "telefono": s.telefono,
        "ciudad": s.ciudad,
        "oficio": s.oficio,
        "descripcion": s.descripcion,
        "perfil_url": s.perfil_url
    })

if __name__ == "__main__":
    app.run(debug=True)
