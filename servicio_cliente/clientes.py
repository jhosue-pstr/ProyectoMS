import mysql.connector
import json
from consul import Consul

consul = Consul()

# Obtener configuración de base de datos desde Consul
def obtener_config_db(servicio):
    _, data = consul.kv.get("servicio_configuracion")
    if not data:
        raise ValueError("No se puede obtener la configuración de Consul")
    configuracion_json = json.loads(data["Value"].decode('utf-8'))
    servicio_config = configuracion_json.get(servicio, {})
    mysql_config = servicio_config.get("MYSQL", {})
    return {key: mysql_config.get(key, '') for key in ['host', 'user', 'password', 'database']}

def conectar(servicio):
    config_db = obtener_config_db(servicio)
    return mysql.connector.connect(**config_db)



def obtener_clientes():
    try:
        conexion = conectar("servicio_cliente")
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, apellido, dni, correo, telefono, direccion FROM cliente")
        resultado = cursor.fetchall()
        conexion.close()
        return resultado
    except Exception as e:
        return {"error": f"Error al obtener los clientes: {str(e)}"}

def obtener_cliente_por_id(id_cliente):
    try:
        conexion = conectar("servicio_cliente")
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, apellido, correo, telefono, direccion FROM cliente WHERE id = %s", (id_cliente,))
        cliente = cursor.fetchone()
        conexion.close()
        return cliente if cliente else {"error": "Cliente no encontrado"}
    except Exception as e:
        return {"error": f"Error al obtener el cliente: {str(e)}"}

def crear_cliente(datos_cliente):
    try:
        conexion = conectar("servicio_cliente") 
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO cliente (nombre, apellido, dni, correo, telefono, direccion) VALUES (%s, %s, %s, %s, %s, %s)",
            (datos_cliente["nombre"], datos_cliente["apellido"], datos_cliente["dni"],
             datos_cliente["correo"], datos_cliente["telefono"], datos_cliente["direccion"])
        )
        conexion.commit()
        conexion.close()
        return {"mensaje": "Cliente creado correctamente"}
    except Exception as e:
        return {"error": f"Error al crear el cliente: {str(e)}"}



def actualizar_cliente(id_cliente, datos_cliente):
    try:
        conexion = conectar("servicio_cliente")
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE cliente SET nombre = %s, apellido = %s, dni = %s, correo = %s, telefono = %s, direccion = %s WHERE id = %s",
            (datos_cliente["nombre"], datos_cliente["apellido"], datos_cliente["dni"],
             datos_cliente["correo"], datos_cliente["telefono"], datos_cliente["direccion"], id_cliente)
        )
        conexion.commit()
        conexion.close()
        return {"mensaje": "Cliente actualizado correctamente"}
    except Exception as e:
        return {"error": f"Error al actualizar el cliente: {str(e)}"}

def eliminar_cliente(id_cliente):
    try:
        conexion = conectar("servicio_cliente")
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM cliente WHERE id = %s", (id_cliente,))
        conexion.commit()
        conexion.close()
        return {"mensaje": "Cliente eliminado correctamente"}
    except Exception as e:
        return {"error": f"Error al eliminar el cliente: {str(e)}"}
