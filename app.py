from flask import Flask, session, render_template, request, redirect, url_for
import controlador_bookify
import os

app = Flask(__name__)
# Clave secreta necesaria para gestionar sesiones
app.secret_key = os.urandom(24)
# Configuración de la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'bookify_user'  # Usuario de la base de datos
app.config['MYSQL_PASSWORD'] = 'bookify_password'  # Contraseña más segura
app.config['MYSQL_DB'] = 'bookify'
app.config['MYSQL_PORT'] = 3306

@app.route('/', methods=['GET', 'POST'])
@app.route('/iniciar_sesion', methods=['GET', 'POST'])
def iniciar_sesion():
    # Si el usuario ya está logueado, redirigir al panel
    if 'user_id' in session:
        return redirect(url_for('panel'))
    
    if request.method == 'POST':
        usuario = request.form['usuario']
        clave = request.form['clave']
        
        user_id = controlador_bookify.iniciar_sesion(usuario, clave)
        if user_id:
            # Configurar la sesión
            session['user_id'] = user_id
            session['usuario'] = usuario
            session.permanent = True  # Opcional: hace que la sesión dure más tiempo
            
            return redirect(url_for('panel'))
        else:
            return render_template('iniciar_sesion.html', 
                                 error="Credenciales incorrectas")
    return render_template('iniciar_sesion.html')

@app.route('/registrarse', methods=['GET', 'POST'])
def registrarse():
    if request.method == 'POST':
        usuario = request.form['usuario']
        correo = request.form['correo']
        clave = request.form['clave']
        
        exito, mensaje = controlador_bookify.registrarse(usuario, correo, clave)
        if exito:
            return redirect(url_for('iniciar_sesion'))
        else:
            return render_template('registrar_usuario.html', 
                                error=mensaje)
    return render_template('registrar_usuario.html')

@app.route('/panel')
def panel():
    # Verificar si el usuario está logueado
    if 'user_id' not in session:
        return redirect(url_for('iniciar_sesion'))
    
    # Obtener datos del usuario si es necesario
    usuario = session.get('usuario')
    return render_template('panel.html', usuario=usuario)

@app.route('/cerrar_sesion')
def cerrar_sesion():
    # Eliminar la información de la sesión
    session.pop('user_id', None)
    session.pop('usuario', None)
    return redirect(url_for('iniciar_sesion'))

@app.route('/agregar-libro', methods=['GET', 'POST'])
def agregar_libro():
    if 'user_id' not in session:
        return redirect(url_for('iniciar_sesion'))
        
    if request.method == 'POST':
        titulo = request.form['titulo']
        id_autor = request.form['autor']
        id_genero = request.form['genero']
        id_editorial = request.form['editorial']
        precio = request.form['precio']
        stock = request.form.get('stock', 0)
        
        exito, mensaje = controlador_bookify.agregar_libro(titulo, id_autor, id_genero, id_editorial, precio, stock)
        if exito:
            return redirect(url_for('panel'))
        else:
            return render_template('agregar_libro.html', error=mensaje)
            
    # Obtener los datos para poblar los select
    autores = controlador_bookify.obtener_autores()
    generos = controlador_bookify.obtener_generos()
    editoriales = controlador_bookify.obtener_editoriales()
    
    return render_template('agregar_libro.html', 
                          autores=autores, 
                          generos=generos, 
                          editoriales=editoriales)

@app.route('/libros-por-autor/<int:id_autor>')
def libros_por_autor(id_autor):
    if 'user_id' not in session:
        return redirect(url_for('iniciar_sesion'))
        
    libros = controlador_bookify.obtener_libros_por_autor(id_autor)
    autor = next((a for a in controlador_bookify.obtener_autores() if a['id'] == id_autor), None)
    
    return render_template('libros_por_autor.html', libros=libros, autor=autor)

@app.route('/buscar-libro', methods=['GET'])
def buscar_libro():
    consulta = request.args.get('consulta', '')
    resultados = []
    
    if consulta:
        resultados = controlador_bookify.buscar_libros(consulta)
    
    return render_template('buscar_libro.html', resultados=resultados, consulta=consulta)

@app.route('/vender-libro', methods=['GET', 'POST'])
def vender_libro():
    if 'user_id' not in session:
        return redirect(url_for('iniciar_sesion'))
        
    if request.method == 'POST':
        id_libro = request.form['libro']
        cantidad = int(request.form['cantidad'])
        id_cliente = session['user_id']
        
        exito, mensaje = controlador_bookify.registrar_venta(id_libro, cantidad, id_cliente)
        if exito:
            return render_template('vender_libro.html', mensaje="Venta registrada exitosamente")
        else:
            return render_template('vender_libro.html', error=mensaje)
    
    # Obtener los libros disponibles
    libros = controlador_bookify.obtener_libros_disponibles()
    return render_template('vender_libro.html', libros=libros)

if __name__ == '__main__':
    app.run(debug=True)