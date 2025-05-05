import mysql.connector
import json
from consul import Consul
import requests
from tenacity import retry, stop_after_attempt, wait_fixed

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





# def obtener_cliente_por_id(id_cliente):
#     try:
#         url_cliente = obtener_direccion_servicio("servicio_cliente")
#         response = requests.get(f"{url_cliente}/clientes/{id_cliente}")
#         if response.status_code == 200:
#             return response.json()
#         else:
#             return {"error": "No se pudo obtener el cliente"}
#     except Exception as e:
#         return {"error": f"Error al consultar el cliente: {str(e)}"}


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def obtener_cliente_por_id(id_cliente):
    try:
        url_cliente = obtener_direccion_servicio("servicio_cliente")
        response = requests.get(f"{url_cliente}/clientes/{id_cliente}", timeout=3)
        response.raise_for_status() 
        return response.json()
    except Exception as e:
        raise Exception(f"No se pudo obtener datos del cliente (microservicio caído): {str(e)}")

try:
    cliente = obtener_cliente_por_id(1)
except Exception as e:
    print("Error:", e)


def obtener_ventas():
    try:
        conexion = conectar("servicio_venta")
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id, id_cliente, fecha, total FROM venta")
        ventas = cursor.fetchall()
        conexion.close()

        for venta in ventas:
            cliente_info = obtener_cliente_por_id(venta['id_cliente'])
            venta['cliente'] = cliente_info

        return ventas
    except Exception as e:
        return {"error": f"error al obtener los ventas: {str(e)}"}






def obtener_venta_por_id(id_venta):
    try:
        conexion = conectar("servicio_venta")
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id ,id_cliente, fecha, total  FROM venta WHERE id = %s", (id_venta,))
        venta = cursor.fetchone()
        conexion.close()

        if venta:
            cliente_info = obtener_cliente_por_id(venta['id_cliente'])
            venta['cliente'] = cliente_info
        return venta
    except Exception as e:
        return {"error": f"error al obtener el venta: {str(e)}"}




def crear_venta(datos_venta):
    try:
        conexion = conectar("servicio_venta") 
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO venta (id_cliente, fecha, total ) VALUES (%s, %s, %s)",
            (datos_venta["id_cliente"], datos_venta["fecha"], datos_venta["total"],
             )
        )
        conexion.commit()
        conexion.close()
        return {"mensaje": "venta creado correctamente"}
    except Exception as e:
        return {"error": f"Error al crear el venta: {str(e)}"}

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





def obtener_ventas():
    try:
        conexion = conectar("servicio_venta")
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id, id_cliente, fecha, total FROM venta")
        ventas = cursor.fetchall()
        conexion.close()

        for venta in ventas:
            cliente_info = obtener_cliente_por_id(venta['id_cliente'])
            venta['cliente'] = cliente_info

        return ventas
    except Exception as e:
        return {"error": f"error al obtener los ventas: {str(e)}"}






def obtener_venta_por_id(id_venta):
    try:
        conexion = conectar("servicio_venta")
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id ,id_cliente, fecha, total  FROM venta WHERE id = %s", (id_venta,))
        venta = cursor.fetchone()
        conexion.close()

        if venta:
            cliente_info = obtener_cliente_por_id(venta['id_cliente'])
            venta['cliente'] = cliente_info
        return venta
    except Exception as e:
        return {"error": f"error al obtener el venta: {str(e)}"}




def crear_venta(datos_venta):
    try:
        conexion = conectar("servicio_venta") 
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO venta (id_cliente, fecha, total ) VALUES (%s, %s, %s)",
            (datos_venta["id_cliente"], datos_venta["fecha"], datos_venta["total"],
             )
        )
        conexion.commit()
        conexion.close()
        return {"mensaje": "venta creado correctamente"}
    except Exception as e:
        return {"error": f"Error al crear el venta: {str(e)}"}



def actualizar_venta(id_venta , datos_venta):
    try:
        conexion = conectar("servicio_venta")
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE venta SET id_cliente = %s, fecha = %s, total = %s WHERE id = %s",
            (datos_venta["id_cliente"], datos_venta["fecha"], datos_venta["total"], id_venta )
        )
        conexion.commit()
        conexion.close()
        return {"mensaje": "venta actualizado correctamente"}
    except Exception as e:
        return {"error": f"Error al actualizar el venta: {str(e)}"}






def eliminar_venta(id_venta):
    try:
        conexion = conectar("servicio_venta")
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM venta WHERE id = %s", (id_venta,))
        conexion.commit()
        conexion.close()
        return {"mensaje": "venta eliminado correctamente"}
    except Exception as e:
        return {"error": f"Error al eliminar el venta: {str(e)}"}
