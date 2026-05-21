import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# IMPORTANTE: Definimos la carpeta templates explícitamente
app = Flask(__name__, template_folder='templates')
CORS(app)

# Configuración de base de datos compatible con Render
db_path = os.path.join(os.path.dirname(__file__), 'soluciones.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de Usuario
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefono = db.Column(db.String(50))
    ciudad = db.Column(db.String(100))
    oficio = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    experiencia = db.Column(db.String(100))
    foto_perfil = db.Column(db.String(300))

# Crear tablas
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/buscar', methods=['GET'])
def buscar():
    oficio = request.args.get('oficio', '')
    ciudad = request.args.get('ciudad', '')
    stmt = Usuario.query
    if oficio: stmt = stmt.filter(Usuario.oficio == oficio)
    if ciudad: stmt = stmt.filter(Usuario.ciudad.like(f"%{ciudad}%"))
    
    usuarios = stmt.all()
    return jsonify([{
        "nombre": u.nombre, "apellido": u.apellido, "oficio": u.oficio,
        "ciudad": u.ciudad, "experiencia": u.experiencia,
        "descripcion": u.descripcion
    } for u in usuarios])

if __name__ == '__main__':
    app.run()
