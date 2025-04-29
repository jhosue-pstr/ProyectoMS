#app.py producto

from flask import Flask,jsonify,request
from consul import Consul
import productos
from productos import actualizar_stock_producto

app = Flask(__name__)
consul_producto = Consul()

def registrar_en_consul():
    consul_producto.agent.service.register(
        "servicio_producto",
        service_id="servicio_producto_5002",
        port=5002,
        tags=["producto"]
    )

registrar_en_consul()

@app.route("/productos")
def listar_productos():
    return jsonify(productos.obtener_productos())



@app.route("/productos/<int:id_producto>", methods=["GET"])
def obtener_producto(id_producto):
    return jsonify(productos.obtener_producto_por_id(id_producto))

@app.route("/productos", methods=["POST"])
def crear_producto():
    datos = request.get_json()
    return jsonify(productos.crear_producto(datos))

@app.route("/productos/<int:id_producto>", methods=["PUT"])
def actualizar_producto(id_producto):
    datos = request.get_json()
    return jsonify(productos.actualizar_producto(id_producto, datos))

@app.route("/productos/<int:id_producto>", methods=["DELETE"])
def eliminar_producto(id_producto):
    return jsonify(productos.eliminar_producto(id_producto))

















@app.route("/actualizar_stock", methods=["POST"])
def actualizar_stock():
    datos = request.get_json()
    id_producto = datos["id_producto"]
    cantidad_vendida = datos["cantidad_vendida"]
    
    resultado = actualizar_stock_producto(id_producto, cantidad_vendida)
    
    if "error" in resultado:
        return jsonify(resultado), 400
    
    return jsonify(resultado), 200








if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",port=5002)