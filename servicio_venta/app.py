#app.py venta
from flask import Flask,jsonify,request
from consul import Consul
import ventas
import ventasDetalle
from ventasDetalle import crear_ventas_detalles


app = Flask(__name__)
consul_cliente = Consul()

def registrar_en_consul():
    consul_cliente.agent.service.register(
        "servicio_venta",
        service_id="servicio_venta_5003",
        port=5002,
        tags=["venta"]
    )

registrar_en_consul()

@app.route("/ventas", methods=["GET"])
def listar_ventas():
    return jsonify(ventas.obtener_ventas())

@app.route("/ventas/<int:id_venta>", methods=["GET"])
def obtener_venta(id_venta):
    return jsonify(ventas.obtener_venta_por_id(id_venta))

@app.route("/ventas", methods=["POST"])
def crear_venta():
    datos = request.get_json()
    return jsonify(ventas.crear_venta(datos))

@app.route("/ventas/<int:id_venta>", methods=["PUT"])
def actualizar_venta(id_venta):
    datos = request.get_json()
    return jsonify(ventas.actualizar_venta(id_venta, datos))

@app.route("/ventas/<int:id_venta>", methods=["DELETE"])
def eliminar_venta(id_venta):
    return jsonify(ventas.eliminar_venta(id_venta))

#======================Detalles de Ventas======================#

@app.route("/ventasDetalle", methods=["GET"])
def listar_ventasDetalle():
    try:
        ventas = ventasDetalle.obtener_ventas_detalle()
        return jsonify(ventas), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/ventasDetalle/<int:id_detalle>", methods=["GET"])
def obtener_ventasDetalle_por_id(id_detalle):
    try:
        venta_detalle = ventasDetalle.obtener_ventas_detalles_por_id(id_detalle)
        return jsonify(venta_detalle), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/ventasDetalle/<int:id_cliente>", methods=["GET"])
def obtener_cliente(id_cliente):
    try:
        cliente = ventasDetalle.obtener_cliente_por_id(id_cliente)
        if cliente:
            return jsonify(cliente), 200
        else:
            return jsonify({"error": "Cliente no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/detalle_venta', methods=['POST'])
def crear_detalle_venta():
    datos_detalle_venta = request.get_json()  
    return crear_ventas_detalles(datos_detalle_venta)


if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=5003)