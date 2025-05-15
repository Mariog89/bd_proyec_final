from bd import obtener_conexion
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import mysql.connector

# Configuración de logging para ayudar a depurar
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def iniciar_sesion(usuario, clave):
    try:
        conexion = obtener_conexion()
        if not conexion:
            logging.error("No se pudo establecer la conexión a la base de datos")
            return None
            
        cursor = conexion.cursor()
        cursor.execute("SELECT id, clave FROM clientes WHERE usuario = %s", (usuario,))
        resultado = cursor.fetchone()
        cursor.close()
        
        if resultado:
            id_usuario, clave_guardada = resultado
            if check_password_hash(clave_guardada, clave):
                logging.info(f"Inicio de sesión exitoso para usuario: {usuario}")
                return id_usuario  # Retornamos el ID del usuario para la sesión
            else:
                logging.warning(f"Intento de inicio de sesión fallido para usuario: {usuario} - Contraseña incorrecta")
        else:
            logging.warning(f"Intento de inicio de sesión fallido - Usuario no encontrado: {usuario}")
        
        return None  # Credenciales inválidas
    except Exception as e:
        logging.error(f"Error al iniciar sesión: {e}")
        return None
    finally:
        if conexion and conexion.is_connected():
            conexion.close()

def registrarse(usuario, correo, clave):
    try:
        conexion = obtener_conexion()
        if not conexion:
            logging.error("No se pudo establecer la conexión a la base de datos")
            return False, "Error de conexión a la base de datos"
            
        cursor = conexion.cursor()
        # Verificar si usuario ya existe
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE usuario = %s", (usuario,))
        if cursor.fetchone()[0] > 0:
            cursor.close()
            conexion.close()
            logging.warning(f"Intento de registro fallido - Usuario ya existe: {usuario}")
            return False, "El nombre de usuario ya está registrado"
        
        # Verificar si correo ya existe
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE correo = %s", (correo,))
        if cursor.fetchone()[0] > 0:
            cursor.close()
            conexion.close()
            logging.warning(f"Intento de registro fallido - Correo ya existe: {correo}")
            return False, "El correo electrónico ya está registrado"

        # Hash de la contraseña
        clave_hash = generate_password_hash(clave)
        
        cursor.execute(
            "INSERT INTO clientes (usuario, correo, clave) VALUES (%s, %s, %s)",
            (usuario, correo, clave_hash)
        )
        conexion.commit()
        cursor.close()
        conexion.close()
        logging.info(f"Usuario registrado exitosamente: {usuario}")
        return True, "Usuario registrado correctamente"
    except Exception as e:
        logging.error(f"Error al registrar usuario: {e}")
        return False, f"Error al registrar usuario: {e}"

def obtener_autores():
    try:
        conexion = obtener_conexion()
        if not conexion:
            logging.error("No se pudo establecer la conexión a la base de datos")
            return []
            
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, nombre, nacionalidad, DATE_FORMAT(fecha_nacimiento, '%Y-%m-%d') as fecha_nacimiento 
            FROM autores 
            ORDER BY nombre
        """)
        autores = cursor.fetchall()
        cursor.close()
        conexion.close()
        return autores
    except Exception as e:
        logging.error(f"Error al obtener autores: {e}")
        return []

def obtener_generos():
    try:
        conexion = obtener_conexion()
        if not conexion:
            logging.error("No se pudo establecer la conexión a la base de datos")
            return []
            
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre FROM generos ORDER BY nombre")
        generos = cursor.fetchall()
        cursor.close()
        conexion.close()
        return generos
    except Exception as e:
        logging.error(f"Error al obtener géneros: {e}")
        return []

def obtener_editoriales():
    try:
        conexion = obtener_conexion()
        if not conexion:
            logging.error("No se pudo establecer la conexión a la base de datos")
            return []
            
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre FROM editoriales ORDER BY nombre")
        editoriales = cursor.fetchall()
        cursor.close()
        conexion.close()
        return editoriales
    except Exception as e:
        logging.error(f"Error al obtener editoriales: {e}")
        return []

def agregar_libro(titulo, id_autor, id_genero, id_editorial, precio, stock):
    try:
        # Validaciones de tipo de dato y valores para manejo de errores
        precio = float(precio)
        stock = int(stock)
        if not isinstance(precio, (int, float)) or precio <= 0:
            return False, "El precio debe ser un número positivo"
        if not isinstance(stock, int) or stock < 0:
            return False, "El stock debe ser un número entero no negativo"
        if not titulo or not titulo.strip():
            return False, "El título no puede estar vacío"
        
        conexion = obtener_conexion()
        if not conexion:
            logging.error("No se pudo establecer la conexión a la base de datos")
            return False, "Error de conexión a la base de datos"
            
        cursor = conexion.cursor()
        # Validar que existan autor, género y editorial
        cursor.execute("SELECT COUNT(*) FROM autores WHERE id = %s", (id_autor,))
        if cursor.fetchone()[0] == 0:
            cursor.close()
            conexion.close()
            return False, "El autor seleccionado no existe"
            
        cursor.execute("SELECT COUNT(*) FROM generos WHERE id = %s", (id_genero,))
        if cursor.fetchone()[0] == 0:
            cursor.close()
            conexion.close()
            return False, "El género seleccionado no existe"
            
        cursor.execute("SELECT COUNT(*) FROM editoriales WHERE id = %s", (id_editorial,))
        if cursor.fetchone()[0] == 0:
            cursor.close()
            conexion.close()
            return False, "La editorial seleccionada no existe"
        
        # Insertar el libro
        cursor.execute(
            "INSERT INTO libros (titulo, id_autor, id_genero, id_editorial, precio, stock) VALUES (%s, %s, %s, %s, %s, %s)",
            (titulo, id_autor, id_genero, id_editorial, precio, stock)
        )
        conexion.commit()
        cursor.close()
        conexion.close()
        logging.info(f"Libro agregado exitosamente: {titulo}")
        return True, "Libro agregado correctamente"
    except Exception as e:
        logging.error(f"Error al agregar libro: {e}")
        return False, f"Error al agregar libro: {e}"

def buscar_libros(consulta):
    try:
        conexion = obtener_conexion()
        if not conexion:
            logging.error("No se pudo establecer la conexión a la base de datos")
            return []
            
        cursor = conexion.cursor(dictionary=True)
        # Buscar por título, autor o editorial
        busqueda = f"%{consulta}%"
        cursor.execute("""
            SELECT l.id, l.titulo, a.nombre AS autor, g.nombre AS genero, 
                   e.nombre AS editorial, l.precio, l.stock
            FROM libros l
            JOIN autores a ON l.id_autor = a.id
            JOIN generos g ON l.id_genero = g.id
            JOIN editoriales e ON l.id_editorial = e.id
            WHERE l.titulo LIKE %s OR a.nombre LIKE %s OR e.nombre LIKE %s
            ORDER BY l.titulo
        """, (busqueda, busqueda, busqueda))
        
        resultados = cursor.fetchall()
        cursor.close()
        conexion.close()
        logging.info(f"Búsqueda realizada: '{consulta}' - Resultados encontrados: {len(resultados)}")
        return resultados
    except Exception as e:
        logging.error(f"Error al buscar libros: {e}")
        return []

def obtener_libros_disponibles():
    try:
        conexion = obtener_conexion()
        if not conexion:
            logging.error("No se pudo establecer la conexión a la base de datos")
            return []
            
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT l.id, l.titulo, a.nombre AS autor, l.precio, l.stock
            FROM libros l
            JOIN autores a ON l.id_autor = a.id
            WHERE l.stock > 0
            ORDER BY l.titulo
        """)
        
        libros = cursor.fetchall()
        cursor.close()
        conexion.close()
        return libros
    except Exception as e:
        logging.error(f"Error al obtener libros disponibles: {e}")
        return []

def registrar_venta(id_libro, cantidad, id_cliente):
    try:
        # Validaciones de tipo de dato y valores
        if not isinstance(cantidad, int) or cantidad <= 0:
            return False, "La cantidad debe ser un número entero positivo"

        conexion = obtener_conexion()
        if not conexion:
            logging.error("No se pudo establecer la conexión a la base de datos")
            return False, "Error de conexión a la base de datos"
            
        cursor = conexion.cursor()
        
        try:
            # Usar el procedimiento almacenado sp_registrar_venta
            cursor.callproc('sp_registrar_venta', (id_libro, id_cliente, cantidad))
            conexion.commit()
            logging.info(f"Venta registrada exitosamente: Libro ID {id_libro}, Cantidad {cantidad}")
            return True, "Venta registrada correctamente"
            
        except mysql.connector.Error as e:
            conexion.rollback()
            if e.errno == 1644:  # Código de error para SIGNAL SQLSTATE
                return False, "No hay suficiente stock disponible"
            logging.error(f"Error al registrar venta: {e}")
            return False, f"Error al registrar venta: {str(e)}"
    except Exception as e:
        logging.error(f"Error al registrar venta: {e}")
        return False, f"Error al registrar venta: {str(e)}"
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()

def obtener_libros_por_autor(id_autor):
    try:
        conexion = obtener_conexion()
        if not conexion:
            logging.error("No se pudo establecer la conexión a la base de datos")
            return []
            
        cursor = conexion.cursor(dictionary=True)
        
        # Usar el procedimiento almacenado sp_get_libros_por_autor
        cursor.callproc('sp_get_libros_por_autor', (id_autor,))
        
        # Obtener resultados del procedimiento almacenado
        for result in cursor.stored_results():
            libros = result.fetchall()
            
        cursor.close()
        conexion.close()
        return libros
    except Exception as e:
        logging.error(f"Error al obtener libros por autor: {e}")
        return []

def obtener_libro(id_libro):
    try:
        cursor = obtener_conexion().cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM libros WHERE id = %s
        """, (id_libro,))
        libro = cursor.fetchone()
        cursor.close()
        return libro
    except Exception as e:
        print(f"Error al obtener libro: {e}")
        return None

def actualizar_libro(id_libro, datos):
    try:
        # Validar precio positivo
        precio = float(datos['precio'])
        if precio <= 0:
            return False, "El precio debe ser un valor positivo"
        
        # Validar stock no negativo
        stock = int(datos['stock'])
        if stock < 0:
            return False, "El stock no puede ser negativo"
        
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        cursor.execute("""
            UPDATE libros 
            SET titulo = %s, 
                id_autor = %s, 
                id_genero = %s, 
                id_editorial = %s, 
                precio = %s, 
                stock = %s
            WHERE id = %s
        """, (
            datos['titulo'],
            datos['id_autor'],
            datos['id_genero'],
            datos['id_editorial'],
            precio,
            stock,
            id_libro
        ))
        
        conexion.commit()
        cursor.close()
        
        return True, "Libro actualizado correctamente"
        
    except ValueError:
        return False, "El precio y stock deben ser valores numéricos válidos"
    except Exception as e:
        print(f"Error al actualizar libro: {e}")
        return False, "Error al actualizar el libro"    

def obtener_libro(id_libro):
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM libros WHERE id = %s
        """, (id_libro,))
        libro = cursor.fetchone()
        cursor.close()
        conexion.close()
        return libro
    except Exception as e:
        logging.error(f"Error al obtener libro: {e}")
        return None

def actualizar_libro(id_libro, datos):
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE libros 
            SET titulo = %s, id_autor = %s, id_genero = %s, 
                id_editorial = %s, precio = %s, stock = %s
            WHERE id = %s
        """, (datos['titulo'], datos['id_autor'], datos['id_genero'],
              datos['id_editorial'], datos['precio'], datos['stock'], id_libro))
        conexion.commit()
        cursor.close()
        conexion.close()
        return True, "Libro actualizado correctamente"
    except Exception as e:
        logging.error(f"Error al actualizar libro: {e}")
        return False, "Error al actualizar el libro"

def eliminar_libro(id_libro):
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        
        # Verificar si el libro tiene ventas asociadas
        cursor.execute("SELECT COUNT(*) FROM ventas WHERE id_libro = %s", (id_libro,))
        if cursor.fetchone()[0] > 0:
            return False, "No se puede eliminar el libro porque tiene ventas asociadas"
        
        cursor.execute("DELETE FROM libros WHERE id = %s", (id_libro,))
        conexion.commit()
        cursor.close()
        conexion.close()
        return True, "Libro eliminado correctamente"
    except Exception as e:
        logging.error(f"Error al eliminar libro: {e}")
        return False, "Error al eliminar el libro"

def obtener_todos_libros():
    try:
        conexion = obtener_conexion()
        with conexion.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT l.id, l.titulo, l.precio, l.stock,
                       a.nombre as autor, g.nombre as genero, e.nombre as editorial
                FROM libros l
                INNER JOIN autores a ON l.id_autor = a.id
                INNER JOIN generos g ON l.id_genero = g.id
                INNER JOIN editoriales e ON l.id_editorial = e.id
                ORDER BY l.titulo
            """)
            libros = cursor.fetchall()
        return libros
    except Exception as e:
        logging.error(f"Error al obtener libros: {e}")
        return []

def agregar_autor(nombre, nacionalidad, fecha_nacimiento):
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("""
                INSERT INTO autores (nombre, nacionalidad, fecha_nacimiento)
                VALUES (%s, %s, %s)
            """, (nombre, nacionalidad, fecha_nacimiento))
        conexion.commit()
        return True, "Autor agregado correctamente"
    except Exception as e:
        logging.error(f"Error al agregar autor: {e}")
        return False, "Error al agregar el autor"

def eliminar_autor(id_autor):
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            # Verificar si hay libros asociados
            cursor.execute("SELECT COUNT(*) FROM libros WHERE id_autor = %s", (id_autor,))
            if cursor.fetchone()[0] > 0:
                return False, "No se puede eliminar el autor porque tiene libros asociados"
            
            cursor.execute("DELETE FROM autores WHERE id = %s", (id_autor,))
        conexion.commit()
        return True, "Autor eliminado correctamente"
    except Exception as e:
        logging.error(f"Error al eliminar autor: {e}")
        return False, "Error al eliminar el autor"