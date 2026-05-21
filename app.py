from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__, template_folder='templates')
CORS(app)

# Base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///soluciones_locales_v2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Lista completa de 100+ oficios
OFICIOS = sorted([
    "Electricista", "Plomero", "Albañil", "Carpintero", "Pintor", "Herrero", "Jardinero", 
    "Mecánico Automotriz", "Técnico de PCs", "Técnico de Celulares", "Diseñador Gráfico", 
    "Programador Android", "Desarrollador Web", "Fotógrafo", "Videógrafo", "Chofer Privado", 
    "Delivery", "Profesor Particular", "Tatuador", "Peluquero", "Barbero", "Manicurista", 
    "Maquilladora", "Fisioterapeuta", "Enfermera", "Masajista", "Cocinero", "Pastelero", 
    "Limpieza", "Técnico Aire Acondicionado", "Cerrajero", "Tapicero", "Vidriero", 
    "Mudanzas", "Contador", "Abogado", "Arquitecto", "Ingeniero", "Sastre", "Veterinario", 
    "Paseador de Perros", "Animador", "DJ", "Instalador de Cámaras", "Reparador Electrodomésticos", 
    "Gasista", "Techista", "Colocador de Pisos", "Yesero", "Fumigador", "Lavador de Autos", 
    "Personal Trainer", "Instructor de Yoga", "Nutricionista", "Psicólogo", "Profesor de Música", 
    "Carpintero de Aluminio", "Decorador", "Editor de Video", "Community Manager", "Seguridad", 
    "Guía Turístico", "Impermeabilizador", "Instalador Paneles Solares", "Luthier", 
    "Maestro Pizzero", "Organizador de Eventos", "Panadero", "Pedicuro", "Pintor Automotriz", 
    "Secretaria Virtual", "Sommelier", "Técnico Refrigeración", "Técnico Electromecánico", 
    "Traductor", "Tornero", "Zinguero", "Vendedor Inmobiliario", "Modelador 3D", "Modisto",
    "Auxiliar Administrativo", "Bartender", "Cajero", "Comprador", "Controlador de Calidad",
    "Cuidado de Ancianos", "Empleado de Comercio", "Esteticista", "Gestor de Trámites",
    "Instalador de Alarmas", "Jardinero de Altura", "Lavandero", "Mecanógrafo",
    "Montajista", "Operador de Máquinas", "Pizzero", "Recepcionista", "Reparador de Computadoras",
    "Sereno", "Soldador", "Técnico en Seguridad e Higiene", "Telefonista", "Vendedor"
])

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/categorias', methods=['GET'])
def obtener_categorias():
    return jsonify(OFICIOS)

if __name__ == '__main__':
    app.run()
