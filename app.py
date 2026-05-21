import os
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder='templates')
CORS(app)

# Configuración
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'soluciones.db')
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo con fotos
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefono = db.Column(db.String(50))
    ciudad = db.Column(db.String(100))
    oficio = db.Column(db.String(100))
    experiencia = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    foto_perfil = db.Column(db.String(300))
    foto_trabajo1 = db.Column(db.String(300))
    foto_trabajo2 = db.Column(db.String(300))
    foto_trabajo3 = db.Column(db.String(300))

with app.app_context():
    db.create_all()

# Funciones de guardado
def guardar_archivo(file):
    if file and file.filename != '':
        filename = uuid.uuid4().hex + "_" + secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(path)
        return filename
    return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.form
    perfil = guardar_archivo(request.files.get('foto_perfil'))
    
    # Manejo de múltiples fotos de trabajos
    trabajos = request.files.getlist('trabajos')
    t1 = guardar_archivo(trabajos[0]) if len(trabajos) > 0 else None
    t2 = guardar_archivo(trabajos[1]) if len(trabajos) > 1 else None
    t3 = guardar_archivo(trabajos[2]) if len(trabajos) > 2 else None

    nuevo = Usuario(
        nombre=data.get('nombre'), apellido=data.get('apellido'),
        email=data.get('email'), telefono=data.get('telefono'),
        ciudad=data.get('ciudad'), oficio=data.get('oficio'),
        experiencia=data.get('experiencia'), descripcion=data.get('descripcion'),
        foto_perfil=perfil, foto_trabajo1=t1, foto_trabajo2=t2, foto_trabajo3=t3
    )
    db.session.add(nuevo)
    db.session.commit()
    return jsonify({"mensaje": "¡Registro exitoso!"})

if __name__ == '__main__':
    app.run()
