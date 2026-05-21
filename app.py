from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='templates')
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///soluciones.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)

# Lista de Ciudades y Oficios
CIUDADES = ["Asunción", "Ciudad del Este", "Encarnación", "Luque", "San Lorenzo", "Capiatá", "Lambaré", "Fernando de la Mora", "Limpio", "Mariano Roque Alonso"]
OFICIOS = sorted(["Electricista", "Plomero", "Albañil", "Carpintero", "Pintor", "Herrero", "Jardinero", "Mecánico", "Técnico de PCs", "Diseñador Gráfico", "Desarrollador Web", "Fotógrafo", "Chofer", "Delivery", "Profesor", "Peluquero", "Masajista", "Cocinero", "Limpieza", "Cerrajero", "Gasista", "Soldador", "Vendedor", "Abogado", "Contador"])

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    apellido = db.Column(db.String(100))
    email = db.Column(db.String(100))
    telefono = db.Column(db.String(50))
    ciudad = db.Column(db.String(100))
    oficio = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    foto = db.Column(db.String(300))

with app.app_context(): db.create_all()

@app.route('/')
def home(): return render_template('index.html')

@app.route('/categorias', methods=['GET'])
def get_categorias(): return jsonify(OFICIOS)

@app.route('/ciudades', methods=['GET'])
def get_ciudades(): return jsonify(CIUDADES)

@app.route('/register', methods=['POST'])
def register():
    data = request.form
    # Aquí iría la lógica de guardar archivo si quieres fotos
    nuevo = Usuario(nombre=data['nombre'], apellido=data['apellido'], email=data['email'], 
                    telefono=data['telefono'], ciudad=data['ciudad'], oficio=data['oficio'], 
                    descripcion=data['descripcion'])
    db.session.add(nuevo)
    db.session.commit()
    return jsonify({"mensaje": "¡Guardado con éxito!"})

if __name__ == '__main__': app.run()
