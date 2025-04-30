#productos.py

import mysql.connector
import json
from consul import Consul

consul = Consul()

def obtener_config_db(servicio):
    _, data = consul.kv.get("servicio_configuracion")
    if not data:
        raise ValueError("No se puede obtener la configuracion de Consul")
    configuracion_json = json.loads(data["Value"].decode('utf-8'))
    servicio_config = configuracion_json.get(servicio,{})
    mysql_config = servicio_config.get("MYSQL",{})
    return {key: mysql_config.get(key, '') for key in ['host','user','password','database']}

def conectar (servicio):
    config_db = obtener_config_db(servicio)
    return mysql.connector.connect(**config_db)

def obtener_productos():
    try:
        conexion = conectar("servicio_producto")
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id , nombre ,descripcion , precio ,stock,categoria FROM producto ")
        resultado = cursor.fetchall()
        conexion.close()
        return resultado
    except Exception as e:
        return{"error": f"error al obtener los productos: {str(e)}"}
    

def obtener_producto_por_id(id_producto):
    try:
        conexion = conectar("servicio_producto")
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id , nombre ,descripcion , precio ,stock,categoria FROM producto WHERE id = %s", (id_producto,))
        producto = cursor.fetchone()
        conexion.close()
        return producto
    except Exception as e:
        return {"error": f"error al obtener el producto: {str(e)}"}




def crear_producto(datos_producto):
    try:
        conexion = conectar("servicio_producto") 
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO producto (nombre ,descripcion , precio ,stock,categoria ) VALUES (%s, %s, %s, %s, %s)",
            (datos_producto["nombre"], datos_producto["descripcion"], datos_producto["precio"],
             datos_producto["stock"], datos_producto["categoria"])
        )
        conexion.commit()
        conexion.close()
        return {"mensaje": "producto creado correctamente"}
    except Exception as e:
        return {"error": f"Error al crear el producto: {str(e)}"}

def actualizar_producto(id_producto , datos_producto):
    try:
        conexion = conectar("servicio_producto")
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE producto SET nombre = %s, descripcion = %s, precio = %s, stock = %s, categoria = %s WHERE id = %s",
            (datos_producto["nombre"], datos_producto["descripcion"], datos_producto["precio"],
             datos_producto["stock"], datos_producto["categoria"], id_producto )
        )
        conexion.commit()
        conexion.close()
        return {"mensaje": "producto actualizado correctamente"}
    except Exception as e:
        return {"error": f"Error al actualizar el producto: {str(e)}"}

def eliminar_producto(id_producto):
    try:
        conexion = conectar("servicio_producto")
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM producto WHERE id = %s", (id_producto,))
        conexion.commit()
        conexion.close()
        return {"mensaje": "producto eliminado correctamente"}
    except Exception as e:
        return {"error": f"Error al eliminar el producto: {str(e)}"}













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
