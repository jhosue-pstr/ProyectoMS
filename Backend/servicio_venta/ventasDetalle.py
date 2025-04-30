import mysql.connector
import json
from consul import Consul
import requests
from decimal import Decimal



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
        producto = obtener_producto_por_id(id_producto)
        if "error" in producto:
            return producto 

        nuevo_stock = producto['stock'] - cantidad_vendida

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

        venta_info = obtener_venta_por_id(venta_detalle['id_venta'])
        venta_detalle['venta'] = venta_info

        if venta_info and 'id_cliente' in venta_info:
            cliente_info = obtener_cliente_por_id(venta_info['id_cliente'])
            venta_detalle['venta']['cliente'] = cliente_info

        return venta_detalle

    except Exception as e:
        return {"error": f"Error al obtener detalle de venta por ID: {str(e)}"}


from decimal import Decimal

def crear_ventas_detalles(datos_detalle_venta):
    try:
        # Conectar a la base de datos de ventas
        try:
            conexion = conectar("servicio_venta")
            cursor = conexion.cursor()
        except Exception as e:
            return {"error": f"Error al conectar con la base de datos: {str(e)}"}

        # Obtener la información del producto
        try:
            id_producto = datos_detalle_venta["id_producto"]
            producto_info = obtener_producto_por_id(id_producto)
        except Exception as e:
            conexion.close()
            return {"error": f"Error al obtener el producto: {str(e)}"}

        if "error" in producto_info:
            conexion.close()
            return {"error": f"Error desde microservicio producto: {producto_info['error']}"}

        # Calcular subtotal
        try:
            precio_unitario = Decimal(str(producto_info["precio"]))
            cantidad = Decimal(str(datos_detalle_venta["cantidad"]))
            subtotal = round(cantidad * precio_unitario, 2)
        except Exception as e:
            conexion.close()
            return {"error": f"Error al calcular subtotal: {str(e)}"}

        # Insertar el detalle de venta
        try:
            cursor.execute(
                "INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario, subtotal) VALUES (%s, %s, %s, %s, %s)",
                (
                    datos_detalle_venta["id_venta"],
                    id_producto,
                    int(cantidad),
                    float(precio_unitario),
                    float(subtotal)
                )
            )
            conexion.commit()
        except Exception as e:
            conexion.rollback()
            conexion.close()
            return {"error": f"Error al insertar detalle de venta en base de datos: {str(e)}"}

        # Actualizar el stock del producto
        try:
            resultado_actualizacion_stock = actualizar_stock_producto(id_producto, int(cantidad))
            if "error" in resultado_actualizacion_stock:
                conexion.close()
                return {"error": f"Error al actualizar el stock: {resultado_actualizacion_stock['error']}"}
        except Exception as e:
            conexion.close()
            return {"error": f"Error al llamar a actualizar_stock_producto: {str(e)}"}

        # Actualizar el total de la venta
        try:
            cursor.execute(
                "SELECT SUM(subtotal) FROM detalle_venta WHERE id_venta = %s", 
                (datos_detalle_venta["id_venta"],)
            )
            total_venta = cursor.fetchone()[0] or Decimal("0.00")
            total_con_iva = total_venta * Decimal("1.18")

            cursor.execute(
                "UPDATE venta SET total = %s WHERE id = %s",
                (round(total_con_iva, 2), datos_detalle_venta["id_venta"])
            )
            conexion.commit()
        except Exception as e:
            conexion.rollback()
            conexion.close()
            return {"error": f"Error al actualizar el total de la venta: {str(e)}"}

        # Cerrar conexión final
        conexion.close()
        return {"mensaje": "Detalle de venta creado, stock actualizado y total de venta ajustado correctamente"}

    except Exception as e:
        return {"error": f"Error inesperado: {str(e)}"}



def actualizar_venta_detalle(id_detalle, nuevos_datos):
    try:
        try:
            conexion = conectar("servicio_venta")
            cursor = conexion.cursor()
        except Exception as e:
            return {"error": f"Error al conectar con la base de datos: {str(e)}"}

        try:
            id_producto = nuevos_datos["id_producto"]
            producto_info = obtener_producto_por_id(id_producto)
        except Exception as e:
            return {"error": f"Error al obtener el producto: {str(e)}"}

        if "error" in producto_info:
            return {"error": f"Error desde microservicio producto: {producto_info['error']}"}

        try:
            precio_unitario = float(producto_info["precio"])
            cantidad = float(nuevos_datos["cantidad"])
            subtotal = round(cantidad * precio_unitario, 2)
        except Exception as e:
            return {"error": f"Error al calcular subtotal: {str(e)}"}

        try:
            cursor.execute(
                "UPDATE detalle_venta SET id_venta = %s, id_producto = %s, cantidad = %s, precio_unitario = %s, subtotal = %s WHERE id_detalle = %s",
                (
                    nuevos_datos["id_venta"],
                    id_producto,
                    cantidad,
                    precio_unitario,
                    subtotal,
                    id_detalle
                )
            )
            conexion.commit()
        except Exception as e:
            conexion.rollback()
            return {"error": f"Error al actualizar el detalle de venta en base de datos: {str(e)}"}
        finally:
            conexion.close()
        try:
            resultado_actualizacion_stock = actualizar_stock_producto(id_producto, cantidad)
            if "error" in resultado_actualizacion_stock:
                return {"error": f"Error al actualizar el stock: {resultado_actualizacion_stock['error']}"}
        except Exception as e:
            return {"error": f"Error al llamar a actualizar_stock_producto: {str(e)}"}

        return {"mensaje": "Detalle de venta actualizado y stock modificado correctamente"}

    except Exception as e:
        return {"error": f"Error inesperado: {str(e)}"}


def eliminar_ventas_detallle(id_detalle_producto):
    try:
        conexion = conectar("servicio_venta")
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM  detalle_venta WHERE id = %s", (id_detalle_producto,))
        conexion.commit()
        conexion.close()
        return {"mensaje": "detalle de venta eliminado correctamente"}
    except Exception as e:
        return {"error": f"Error al eliminar el detalle de venta: {str(e)}"}



