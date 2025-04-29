#app.py cliente

from flask import Flask,jsonify,request
from consul import Consul
import clientes

app = Flask(__name__)
consul_cliente = Consul()

def registrar_en_consul():
    consul_cliente.agent.service.register(
        "servicio_cliente",
        service_id="servicio_cliente_5001",
        port=5001,
        tags=["cliente"]
    )

registrar_en_consul()

@app.route("/clientes")
def listar_clientes():
    return jsonify(clientes.obtener_clientes())



@app.route("/clientes/<int:id_cliente>", methods=["GET"])
def obtener_cliente(id_cliente):
    return jsonify(clientes.obtener_cliente_por_id(id_cliente))

@app.route("/clientes", methods=["POST"])
def crear_cliente():
    datos = request.get_json()
    return jsonify(clientes.crear_cliente(datos))

@app.route("/clientes/<int:id_cliente>", methods=["PUT"])
def actualizar_cliente(id_cliente):
    datos = request.get_json()
    return jsonify(clientes.actualizar_cliente(id_cliente, datos))

@app.route("/clientes/<int:id_cliente>", methods=["DELETE"])
def eliminar_cliente(id_cliente):
    return jsonify(clientes.eliminar_cliente(id_cliente))



if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=5001)