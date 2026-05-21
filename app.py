from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__, template_folder='templates')
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///soluciones.db'
db = SQLAlchemy(app)

# Listas definitivas
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

with app.app_context(): db.create_all()

@app.route('/')
def home(): return render_template('index.html')

@app.route('/categorias')
def get_cat(): return jsonify(OFICIOS)

@app.route('/ciudades')
def get_ciu(): return jsonify(CIUDADES)

@app.route('/register', methods=['POST'])
def register():
    data = request.form
    nuevo = Usuario(nombre=data.get('nombre'), apellido=data.get('apellido'), email=data.get('email'), 
                    telefono=data.get('telefono'), ciudad=data.get('ciudad'), oficio=data.get('oficio'), 
                    descripcion=data.get('descripcion'))
    db.session.add(nuevo)
    db.session.commit()
    return jsonify({"status": "ok"})

if __name__ == '__main__': app.run()
