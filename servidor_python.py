from flask import Flask, request, jsonify, render_template, make_response
import sqlite3
from datetime import datetime
import pytz
import csv
import io

app = Flask(__name__)

# Ruta para la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para recibir datos del ESP32
@app.route('/datos', methods=['POST'])
def recibir_datos():
    try:
        # Datos recibidos en formato JSON
        data = request.json
        voltaje = data.get('voltaje')
        corriente = data.get('corriente')
        potencia = data.get('potencia')
        energia = data.get('energia')
        frecuencia = data.get('frecuencia')
        pf = data.get('pf')

        # Insertar los datos en la base de datos
        insertar_datos(voltaje, corriente, potencia, energia, frecuencia, pf)

        return jsonify({"message": "Datos recibidos correctamente"}), 200
    except Exception as e:
        print(f"Error al recibir los datos: {e}")
        return jsonify({"message": "Error al recibir los datos"}), 500

# Función para insertar datos en la base de datos
def insertar_datos(voltaje, corriente, potencia, energia, frecuencia, pf):
    try:
        conn = sqlite3.connect('datos_sensores.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS datos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        voltaje REAL,
                        corriente REAL,
                        potencia REAL,
                        energia REAL,
                        frecuencia REAL,
                        pf REAL,
                        timestamp TEXT
                    )''')
        
        # Obtener la hora actual con zona horaria
        time_zone = pytz.timezone('America/Santiago')
        time_now = datetime.now(time_zone).strftime('%Y-%m-%d %H:%M:%S')

        # Insertar los datos
        c.execute('''INSERT INTO datos (voltaje, corriente, potencia, energia, frecuencia, pf, timestamp)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (voltaje, corriente, potencia, energia, frecuencia, pf, time_now))

        conn.commit()
        conn.close()
        print("Datos insertados correctamente")
    except sqlite3.Error as e:
        print(f"Error al insertar datos: {e}")

# Ruta para ver las últimas 10 lecturas
@app.route('/ultimas_lecturas', methods=['GET'])
def ultimas_lecturas():
    try:
        conn = sqlite3.connect('datos_sensores.db')
        c = conn.cursor()
        c.execute("SELECT voltaje, corriente, potencia, energia, frecuencia, pf, timestamp FROM datos ORDER BY id DESC LIMIT 10")
        rows = c.fetchall()
        conn.close()

        ultimas_lecturas = {
            'labels': [row[6] for row in rows],
            'voltaje': [row[0] for row in rows],
            'corriente': [row[1] for row in rows],
            'potencia': [row[2] for row in rows],
            'energia': [row[3] for row in rows],
            'frecuencia': [row[4] for row in rows],
            'pf': [row[5] for row in rows]
        }

        return jsonify(ultimas_lecturas), 200
    except Exception as e:
        print(f"Error al obtener las últimas lecturas: {e}")
        return jsonify({"message": "Error al obtener las últimas lecturas"}), 500

# Ruta para descargar datos en CSV
@app.route('/descargar_csv', methods=['GET'])
def descargar_csv():
    try:
        conn = sqlite3.connect('datos_sensores.db')
        c = conn.cursor()
        c.execute("SELECT * FROM datos")
        rows = c.fetchall()
        conn.close()

        # Crear el archivo CSV en memoria
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Voltaje (V)', 'Corriente (A)', 'Potencia (W)', 'Energía (kWh)', 'Frecuencia (Hz)', 'Factor de Potencia', 'Fecha y Hora'])
        writer.writerows(rows)

        # Crear la respuesta
        output.seek(0)
        return make_response(output.getvalue(), 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': 'attachment; filename=datos_sensores.csv',
        })
    except Exception as e:
        print(f"Error al descargar CSV: {e}")
        return jsonify({"message": "Error al descargar CSV"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
