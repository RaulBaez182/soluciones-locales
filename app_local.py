from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import os
import uuid

app = Flask(__name__)
CORS(app)

# TUS BASES DE DATOS REALES
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///soluciones_locales_v2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# TUS CARPETAS REALES (COMO EN TU CAPTURA)
UPLOAD_PERFILES = os.path.join('uploads', 'perfiles')
UPLOAD_TRABAJOS = os.path.join('uploads', 'trabajos')
UPLOAD_ESTUDIOS = os.path.join('uploads', 'estudios')

app.config['UPLOAD_PERFILES'] = UPLOAD_PERFILES

db = SQLAlchemy(app)

# ======================================
# MODELO DE USUARIO COMPATIBLE
# ======================================
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)
    telefono = db.Column(db.String(50))
    ciudad = db.Column(db.String(100))
    oficio = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    experiencia = db.Column(db.String(100))
    foto_perfil = db.Column(db.String(300))
    verificado = db.Column(db.Boolean, default=False)

# LISTA OFICIAL CON MÁS DE 100 OFICIOS
oficios_lista = sorted([
    "Electricista", "Plomero", "Albañil", "Carpintero", "Pintor", "Herrero", "Jardinero",
    "Mecánico Automotriz", "Técnico de PCs", "Técnico de Celulares", "Diseñador Gráfico",
    "Programador Android", "Desarrollador Web", "Fotógrafo", "Videógrafo", "Chofer Privado",
    "Delivery / Mensajero", "Profesor Particular", "Clases de Inglés", "Tatuador", "Peluquero",
    "Barbero", "Manicurista", "Maquilladora", "Fisioterapeuta", "Enfermera Domiciliaria",
    "Masajista", "Cocinero / Chef", "Pastelero", "Mozo / Camarero", "Limpieza de Hogares",
    "Soporte Técnico Aire Acondicionado", "Cerrajero", "Tapicero", "Vidriero", "Mudanzas",
    "Contador Público", "Abogado Consultor", "Arquitecto", "Ingeniero Civil", "Diseñador de Interiores",
    "Sastre / Costurera", "Veterinario Domiciliario", "Paseador de Perros", "Adiestrador Canino",
    "Animador de Eventos", "DJ", "Instalador de Cámaras de Seguridad", "Reparador de Electrodomésticos",
    "Gasista Matriculado", "Techista", "Colocador de Pisos / Cerámicas", "Yesero", "Fumigador",
    "Lavador de Autos", "Personal Trainer", "Instructor de Yoga", "Nutricionista", "Psicólogo",
    "Profesor de Música", "Afilador de Herramientas", "Boticario", "Carpintero de Aluminio",
    "Decorador de Eventos", "Dibujante Técnico", "Editor de Video", "Especialista SEO", "Guardia de Seguridad",
    "Guía Turístico", "Impermeabilizador", "Instalador de Paneles Solares", "Jardinero de Altura",
    "Luthier", "Maestro Mayor de Obras", "Maestro Pizzero", "Modelista", "Modisto", "Organizador de Bodas",
    "Panadero", "Pedicuro", "Perito Mercantil", "Pintor Automotriz", "Perforador de Pozos de Agua", 
    "Planchadora", "Programador de PLC", "Productor de Seguros", "Reparador de Bicicletas", 
    "Reparador de Calzado", "Reparador de Relojes", "Secretaria Virtual", "Service de Termotanques", 
    "Sommelier", "Técnico en Refrigeración", "Técnico Electromecánico", "Traductor Jurado", "Tornero",
    "Tapizador de Autos", "Zinguero", "Vendedor Inmobiliario", "Modelador 3D", "Community Manager"
])

with app.app_context():
    db.create_all()

def nombre_unico(filename):
    ext = filename.split('.')[-1]
    return f"{uuid.uuid4().hex}.{ext}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/uploads/<path:filename>')
def mostrar_foto(filename):
    return send_from_directory('uploads', filename)

# REGISTRO V2 ASOCIADO A TUS CARPETAS DE FOTOS
@app.route('/register', methods=['POST'])
def register():
    data = request.form
    email = data.get('email')

    if Usuario.query.filter_by(email=email).first():
        return jsonify({"error": "El correo ya está registrado"}), 400

    foto_perfil_path = ""
    if 'foto_perfil' in request.files:
        file = request.files['foto_perfil']
        if file.filename != '':
            filename = nombre_unico(secure_filename(file.filename))
            foto_perfil_path = f"uploads/perfiles/{filename}"
            file.save(os.path.join(app.config['UPLOAD_PERFILES'], filename))

    nuevo = Usuario(
        nombre=data.get('nombre'),
        apellido=data.get('apellido'),
        email=email,
        password=generate_password_hash(data.get('password')),
        telefono=data.get('telefono'),
        ciudad=data.get('ciudad'),
        oficio=data.get('oficio'),
        descripcion=data.get('descripcion'),
        experiencia=data.get('experiencia'),
        foto_perfil=foto_perfil_path
    )
    db.session.add(nuevo)
    db.session.commit()
    return jsonify({"mensaje": "¡Usuario registrado con éxito!"})

# BUSCADOR V2
@app.route('/buscar', methods=['GET'])
def buscar():
    oficio = request.args.get('oficio', '')
    ciudad = request.args.get('ciudad', '')

    stmt = Usuario.query
    if oficio:
        stmt = stmt.filter(Usuario.oficio == oficio)
    if ciudad:
        stmt = stmt.filter(Usuario.ciudad.like(f"%{ciudad}%"))

    usuarios = stmt.all()
    resultado = []
    for u in usuarios:
        resultado.append({
            "id": u.id,
            "nombre": u.nombre,
            "apellido": u.apellido,
            "oficio": u.oficio,
            "ciudad": u.ciudad,
            "experiencia": u.experiencia,
            "descripcion": u.descripcion,
            "foto_perfil": u.foto_perfil,
            "verificado": u.verificado
        })
    return jsonify(resultado)

@app.route('/categorias', methods=['GET'])
def obtener_categorias():
    return jsonify(oficios_lista)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)