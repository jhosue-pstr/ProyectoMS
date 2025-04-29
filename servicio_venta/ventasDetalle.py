import mysql.connector
import json
from consul import Consul
import requests

consul = Consul()

def obtener_config_db(servicio):
    _, data = consul.kv.get("servicio_configuracion")
    if not data:
        raise ValueError("No se puede obtener la configuracion de Consul")
    configuracion_json = json.loads(data["Value"].decode('utf-8'))
    servicio_config = configuracion_json.get(servicio, {})
    mysql_config = servicio_config.get("MYSQL", {})
    return {key: mysql_config.get(key, '') for key in ['host', 'user', 'password', 'database']}

def conectar(servicio):
    config_db = obtener_config_db(servicio)
    return mysql.connector.connect(**config_db)

def obtener_direccion_servicio(servicio):
    index, servicios = consul.catalog.service(servicio)
    if not servicios:
        raise ValueError(f"No se encontró el servicio {servicio} en Consul")
    servicio_info = servicios[0]
    address = servicio_info["ServiceAddress"] or servicio_info["Address"]
    port = servicio_info["ServicePort"]
    return f"http://{address}:{port}"


def obtener_producto_por_id(id_producto):
    try:
        url_producto = obtener_direccion_servicio("servicio_producto")
        response = requests.get(f"{url_producto}/productos/{id_producto}")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "No se pudo obtener el producto"}
    except Exception as e:
        return {"error": f"Error al consultar el producto: {str(e)}"}


def obtener_venta_por_id(id_venta):
    try:
        conexion = conectar("servicio_venta")
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id, fecha, id_cliente, total FROM venta WHERE id = %s", (id_venta,))
        venta = cursor.fetchone()
        conexion.close()
        return venta
    except Exception as e:
        return {"error": f"Error al consultar la venta: {str(e)}"}

def obtener_cliente_por_id(id_cliente):
    try:
        url_cliente = obtener_direccion_servicio("servicio_cliente")
        response = requests.get(f"{url_cliente}/clientes/{id_cliente}")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "No se pudo obtener el cliente"}
    except Exception as e:
        return {"error": f"Error al consultar el cliente: {str(e)}"}

































def actualizar_stock_producto(id_producto, cantidad_vendida):
    try:
        # Primero obtienes el producto
        producto = obtener_producto_por_id(id_producto)
        if "error" in producto:
            return producto  # Si no encuentras el producto, retornas un error

        # Calculas el nuevo stock
        nuevo_stock = producto['stock'] - cantidad_vendida

        # Actualizas el stock en la base de datos
        conexion = conectar("servicio_producto")
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE producto SET stock = %s WHERE id = %s",
            (nuevo_stock, id_producto)
        )
        conexion.commit()
        conexion.close()

        return {"mensaje": "Stock actualizado correctamente"}
    except Exception as e:
        return {"error": f"Error al actualizar el stock: {str(e)}"}


#===================CRUD================================#

def obtener_ventas_detalle():
    try:
        conexion = conectar("servicio_venta")
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id, id_venta, id_producto, cantidad, precio_unitario, subtotal FROM detalle_venta")
        resultado = cursor.fetchall()
        conexion.close()

        for venta in resultado:
            producto_info = obtener_producto_por_id(venta['id_producto'])
            venta['producto'] = producto_info

            venta_info = obtener_venta_por_id(venta['id_venta'])
            venta['venta'] = venta_info

            if venta_info and 'id_cliente' in venta_info:
                cliente_info = obtener_cliente_por_id(venta_info['id_cliente'])
                venta['venta']['cliente'] = cliente_info  

        return resultado
    except Exception as e:
        return {"error": f"error al obtener las ventas detalle: {str(e)}"}




def obtener_ventas_detalles_por_id(id_detalle_producto):
    try:
        conexion = conectar("servicio_venta")
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, id_venta, id_producto, cantidad, precio_unitario, subtotal FROM detalle_venta WHERE id = %s",
            (id_detalle_producto,)
        )
        venta_detalle = cursor.fetchone()
        conexion.close()

        if not venta_detalle:
            return {"error": "No se encontró detalle de venta con ese ID"}

        producto_info = obtener_producto_por_id(venta_detalle['id_producto'])
        venta_detalle['producto'] = producto_info

        # Obtener información de la venta
        venta_info = obtener_venta_por_id(venta_detalle['id_venta'])
        venta_detalle['venta'] = venta_info

        # Obtener información del cliente (si existe)
        if venta_info and 'id_cliente' in venta_info:
            cliente_info = obtener_cliente_por_id(venta_info['id_cliente'])
            venta_detalle['venta']['cliente'] = cliente_info

        return venta_detalle

    except Exception as e:
        return {"error": f"Error al obtener detalle de venta por ID: {str(e)}"}



















def crear_ventas_detalles(datos_detalle_venta):
    try:
        conexion = conectar("servicio_venta") 
        cursor = conexion.cursor()

        # Obtener información del producto
        producto_info = obtener_producto_por_id(datos_detalle_venta["id_producto"])
        if "error" in producto_info:
            return {"error": f"Error al obtener el producto: {producto_info['error']}"}
        
        precio_unitario = float(producto_info["precio"]) 
        cantidad = float(datos_detalle_venta["cantidad"])
        subtotal = round(cantidad * precio_unitario, 2)

        # Insertar el detalle de la venta en la base de datos
        cursor.execute(
            "INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario, subtotal) VALUES (%s, %s, %s, %s, %s)",
            (
                datos_detalle_venta["id_venta"],
                datos_detalle_venta["id_producto"],
                cantidad, 
                precio_unitario,  
                subtotal  
            )
        )
        
        # Llamar a la función para actualizar el stock
        resultado_actualizacion_stock = actualizar_stock_producto(datos_detalle_venta["id_producto"], cantidad)
        if "error" in resultado_actualizacion_stock:
            return {"error": f"Error al actualizar el stock: {resultado_actualizacion_stock['error']}"}

        # Confirmar cambios y cerrar la conexión
        conexion.commit()
        conexion.close()
        
        return {"mensaje": "Detalle de venta creado y stock actualizado correctamente"}
    
    except Exception as e:
        return {"error": f"Error al crear el detalle de venta: {str(e)}"}
