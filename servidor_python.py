from flask import Flask, request, jsonify, render_template, make_response
import requests
from datetime import datetime
import pytz
import csv
import io
import os

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

        # Aquí podrías agregar la lógica para enviar los datos al web service de Render si es necesario

        return jsonify({"message": "Datos recibidos correctamente"}), 200
    except Exception as e:
        print(f"Error al recibir los datos: {e}")
        return jsonify({"message": "Error al recibir los datos"}), 500

# Ruta para ver las últimas 10 lecturas, obteniendo los datos desde el web service en Render
@app.route('/ultimas_lecturas', methods=['GET', 'POST'])
def ultimas_lecturas():
    try:
        # URL del web service en Render que proporciona los datos
        web_service_url = "https://proyecto-lora-sx1278.onrender.com/ultimas_lecturas"
        
        # Realizar la solicitud GET al web service
        response = requests.get(web_service_url)
        
        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            # Parsear los datos recibidos en formato JSON
            datos = response.json()
            
            ultimas_lecturas = {
                'labels': [dato['timestamp'] for dato in datos],
                'voltaje': [dato['voltaje'] for dato in datos],
                'corriente': [dato['corriente'] for dato in datos],
                'potencia': [dato['potencia'] for dato in datos],
                'energia': [dato['energia'] for dato in datos],
                'frecuencia': [dato['frecuencia'] for dato in datos],
                'pf': [dato['pf'] for dato in datos]
            }
            
            return jsonify(ultimas_lecturas), 200
        else:
            print(f"Error al obtener las últimas lecturas desde el web service: {response.status_code}")
            return jsonify({"message": "Error al obtener las últimas lecturas"}), 500
    except Exception as e:
        print(f"Error al obtener las últimas lecturas: {e}")
        return jsonify({"message": "Error al obtener las últimas lecturas"}), 500

# Ruta para descargar datos en CSV
@app.route('/descargar_csv', methods=['GET', 'POST'])
def descargar_csv():
    try:
        # URL del web service en Render que proporciona los datos
        web_service_url = "https://proyecto-lora-sx1278.onrender.com"
        
        # Realizar la solicitud GET al web service
        response = requests.get(web_service_url)
        
        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            # Parsear los datos recibidos en formato JSON
            datos = response.json()
            
            # Crear el archivo CSV en memoria
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Timestamp', 'Voltaje (V)', 'Corriente (A)', 'Potencia (W)', 'Energía (kWh)', 'Frecuencia (Hz)', 'Factor de Potencia'])
            for dato in datos:
                writer.writerow([dato['timestamp'], dato['voltaje'], dato['corriente'], dato['potencia'], dato['energia'], dato['frecuencia'], dato['pf']])

            # Crear la respuesta
            output.seek(0)
            return make_response(output.getvalue(), 200, {
                'Content-Type': 'text/csv',
                'Content-Disposition': 'attachment; filename=datos_sensores.csv',
            })
        else:
            print(f"Error al descargar CSV desde el web service: {response.status_code}")
            return jsonify({"message": "Error al descargar CSV"}), 500
    except Exception as e:
        print(f"Error al descargar CSV: {e}")
        return jsonify({"message": "Error al descargar CSV"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5001)), debug=True)
