from flask import Flask, jsonify
import requests
import base64
import json

app = Flask(__name__)

CONSUL_HOST = "http://localhost:8500"
KEY = "servicio_configuracion"

def obtener_configuracion():
    url = f"{CONSUL_HOST}/v1/kv/{KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        config_json = base64.b64decode(data[0]['Value']).decode('utf-8')
        return json.loads(config_json)
    else:
        return {'error': 'No se pudo obtener la configuración'}

@app.route('/configuracion', methods=['GET'])
def config_servicio():
    config = obtener_configuracion()
    return jsonify(config)

if __name__ == '__main__':
    app.run(debug=True, port=5000)