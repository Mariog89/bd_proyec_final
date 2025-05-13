import mysql.connector
from mysql.connector import Error
from flask import current_app

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB'],
            port=current_app.config['MYSQL_PORT']
        )
        return conexion
    except Error as e:
        current_app.logger.error(f"Error al conectar a MariaDB: {e}")
        return None