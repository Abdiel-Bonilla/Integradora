import psycopg2
from flask import Flask,redirect,render_template,request,url_for, session,flash
from forms import LoginForm
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms.fields import PasswordField,StringField,SubmitField
from wtforms.validators import DataRequired
import db
from forms import UsuariosForm,ProductosForm,VentaForm
from werkzeug.security import generate_password_hash,check_password_hash
from functools import wraps
from datetime import datetime
from flask import send_file
from pdf_utils import generar_pdf
from werkzeug.exceptions import NotFound

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'ciclos'

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirige al login si no está autenticado
    return render_template('base.html')  # Aquí renderiza la página principal del menú


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        conn = db.conectar()
        cursor = conn.cursor()
        cursor.execute('SELECT id_usuario, nombre, contrasena, tipo FROM "Usuario" WHERE nombre = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        db.desconectar(conn)
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]  # Almacena el rol del usuario
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('index'))
        else:
            flash('Nombre de usuario o contraseña incorrectos', 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('login'))

# Asegúrate de usar @role_required en las rutas que necesiten autenticación
def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Por favor, inicia sesión.', 'danger')
                return redirect(url_for('login'))
            if session.get('role') not in roles:
                flash('No tienes permiso para acceder a esta página.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/usuarios')
@role_required(['admin'])
def usuarios():
    # Conectar con la base de datos
    conn= db.conectar()
    #crear un cursor (objeto para recorrer las tablas)
    cursor= conn.cursor()
    # ejecutar una consulta en postgres
    cursor.execute('''SELECT * FROM "Usuario" ORDER BY id_usuario''')
    #recuperar la informacion
    datos = cursor.fetchall()
    #cerrar cursos y conexion a la base de datos
    cursor.close()
    db.desconectar(conn)
    return render_template('usuarios.html', datos=datos)

@app.route('/buscar_usuarios', methods=['POST'])
def buscar_usuarios():
    buscar_texto = request.form['buscar']
    #conectar con la BD
    conn= db.conectar()
    #crear un cursor (objeto para recorrer las tablas)
    cursor= conn.cursor()
    cursor.execute('''
        SELECT * FROM "Usuario"
        WHERE nombre ILIKE %s OR id_usuario::TEXT ILIKE %s
    ''', (f'%{buscar_texto}%', f'%{buscar_texto}%'))
    datos = cursor.fetchall()
    cursor.close()
    db.desconectar(conn)
    return render_template('usuarios.html', datos=datos)

@app.route('/update1_usuarios/<int:id_usuario>', methods=['POST'])
def update1_usuarios(id_usuario):
    # Conectar con la base de datos
    conn = db.conectar()
    # Crear un cursor (objeto para recorrer las tablas)
    cursor = conn.cursor()
    # Recuperar el registro del producto seleccionado
    cursor.execute('''SELECT * FROM "Usuario" WHERE id_usuario=%s''', (id_usuario,))
    datos = cursor.fetchall()
    cursor.close()
    db.desconectar(conn)
    return render_template('editar_usuarios.html', datos=datos)

@app.route('/update2_usuarios/<int:id_usuario>', methods=['POST'])
def update2_usuarios(id_usuario):
    nombre = request.form['nombre']
    apellido_pat = request.form['apellido-pat']
    apellido_mat = request.form['apellido-mat']
    cargo = request.form['tipo']
    contrasena = request.form['contrasena']
    # Conectar con la base de datos
    conn = db.conectar()
    cursor = conn.cursor()
    # Actualizar los datos del usuario en la base de datos
    cursor.execute('''
        UPDATE "Usuario"
        SET nombre=%s, ape_pat=%s, ape_mat=%s, tipo=%s, contrasena=%s
        WHERE id_usuario=%s
    ''', (nombre, apellido_pat, apellido_mat, cargo, contrasena, id_usuario))
    conn.commit()
    cursor.close()
    db.desconectar(conn)
    return redirect(url_for('usuarios'))

@app.route('/registrar_usuario', methods=['GET', 'POST'])
def registrar_usuario():
    form = UsuariosForm()
    if form.validate_on_submit():
        nombre = form.nombre.data
        ape_pat = form.ape_pat.data
        ape_mat = form.ape_mat.data
        tipo = form.tipo.data
        contraseña = generate_password_hash(form.contraseña.data)  # Hashear la contraseña
        # insertar datos
        conn = db.conectar()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO "Usuario" (nombre, ape_pat, ape_mat, tipo, contrasena)
            VALUES (%s, %s, %s, %s, %s)
        ''', (nombre, ape_pat, ape_mat, tipo, contraseña))
        conn.commit()
        cursor.close()
        db.desconectar(conn)
        return render_template('registrar_usuario.html', form=form, success=True)
    return render_template('registrar_usuario.html', form=form, success=False)


@app.route('/delete_usuarios/<int:id_usuario>', methods=['POST'])
def delete_usuarios(id_usuario):
    # Conectar con la base de datos
    conn= db.conectar()
    #crear un cursor (objeto para recorrer las tablas)
    cursor= conn.cursor()
    #Borrar el registro con el id_pais seleccionado
    cursor.execute('''DELETE FROM "Usuario" WHERE id_usuario=%s''',
                    (id_usuario,))
    conn.commit()
    cursor.close()
    db.desconectar(conn)
    return redirect(url_for('index'))

#PRODUCTOOOS

@app.route('/productos')
@role_required(['admin'])
def productos():
    # Conectar con la base de datos
    conn= db.conectar()
    #crear un cursor (objeto para recorrer las tablas)
    cursor= conn.cursor()
    # ejecutar una consulta en postgres
    cursor.execute('''SELECT * FROM consulta_prod ORDER BY id_prod''')
    #recuperar la informacion
    datos = cursor.fetchall()
    #cerrar cursos y conexion a la base de datos
    cursor.close()
    db.desconectar(conn)
    return render_template('productos.html', datos=datos)

@app.route('/buscar_productos', methods=['POST'])
def buscar_productos():
    buscar_texto = request.form['buscar']
    #conectar con la BD
    conn= db.conectar()
    #crear un cursor (objeto para recorrer las tablas)
    cursor= conn.cursor()
    cursor.execute('''
        SELECT * FROM consulta_prod
        WHERE nombre ILIKE %s OR id_prod::TEXT ILIKE %s
    ''', (f'%{buscar_texto}%', f'%{buscar_texto}%'))
    datos = cursor.fetchall()
    cursor.close()
    db.desconectar(conn)
    return render_template('productos.html', datos=datos)

@app.route('/delete_productos/<int:id_prod>', methods=['POST'])
def delete_productos(id_prod):
    # Conectar con la base de datos
    conn = db.conectar()
    cursor = conn.cursor()
    # Borrar el registro con el id_prod seleccionado en la tabla producto
    cursor.execute('''DELETE FROM producto WHERE id_prod=%s''', (id_prod,))
    # Confirmar los cambios
    conn.commit()
    cursor.close()
    db.desconectar(conn)
    return redirect(url_for('productos'))

@app.route('/update1_productos/<int:id_prod>', methods=['POST'])
def update1_productos(id_prod):
    # Conectar con la base de datos
    conn = db.conectar()
    # Crear un cursor (objeto para recorrer las tablas)
    cursor = conn.cursor()
    # Recuperar el registro del producto seleccionado
    cursor.execute('''SELECT * FROM consulta_prod WHERE id_prod=%s''', (id_prod,))
    datos = cursor.fetchall()
    cursor.close()
    db.desconectar(conn)
    return render_template('editar_productos.html', datos=datos)

@app.route('/update2_productos/<int:id_prod>', methods=['POST'])
def update2_productos(id_prod):
    nombre = request.form['nombre']
    cantidad = request.form['cantidad']
    caducidad = request.form['caducidad']
    precio = request.form['precio']
    categoria = request.form['categoria']
    # Conectar con la base de datos
    conn = db.conectar()
    # Crear un cursor (objeto para recorrer las tablas)
    cursor = conn.cursor()
    # Actualizar la tabla producto (no la vista)
    cursor.execute('''
        UPDATE producto
        SET nombre = %s, cantidad = %s, caducidad = %s, precio_cu = %s
        WHERE id_prod = %s
    ''', (nombre, cantidad, caducidad, precio, id_prod))
    # Actualizar la tabla Categoria
    cursor.execute('''
        UPDATE "Categoria"
        SET nombre_ca = %s
        WHERE id_categ = (
            SELECT fk_categoria
            FROM producto
            WHERE id_prod = %s
        )
    ''', (categoria, id_prod))
    conn.commit()
    cursor.close()
    db.desconectar(conn)
    return redirect(url_for('productos'))

@app.route('/registrar_producto', methods=['GET', 'POST'])
def registrar_producto():
    form = ProductosForm()
    if form.validate_on_submit():
        nombre = form.nombre.data
        cantidad = form.cantidad.data
        caducidad = form.caducidad.data
        precio = form.precio.data
        categoria_nombre = form.categoria.data  # Nombre de la categoría ingresado
        # Conectar con la base de datos
        conn = db.conectar()
        cursor = conn.cursor()
        # Verificar si la categoría ya existe
        cursor.execute('SELECT id_categ FROM "Categoria" WHERE nombre_ca = %s', (categoria_nombre,))
        categoria = cursor.fetchone()
        if categoria:
            # Usar el id de la categoría existente
            categoria_id = categoria[0]
        else:
            # Insertar nueva categoría y obtener su id
            cursor.execute('INSERT INTO Categoria (nombre_ca) VALUES (%s) RETURNING id_categ', (categoria_nombre,))
            categoria_id = cursor.fetchone()[0]
        # Insertar el producto con el id de la categoría
        cursor.execute('''
            INSERT INTO producto (nombre, cantidad, caducidad, precio_cu, fk_categoria)
            VALUES (%s, %s, %s, %s, %s)
        ''', (nombre, cantidad, caducidad, precio, categoria_id))
        conn.commit()
        cursor.close()
        db.desconectar(conn)
        return render_template('registrar_producto.html', form=form, success=True)
    return render_template('registrar_producto.html', form=form, success=False)


#VENTAAAS

@app.route('/ventas')
@role_required(['admin', 'cashier'])
def ventas():
    #conectar con la BD
    conn= db.conectar()
    #crear un cursor (objeto para recorrer las tablas)
    cursor= conn.cursor()
    #ejecutar una consulta en postgres
    cursor.execute('''SELECT*FROM ventas_view2 ORDER BY id ''')
    #recuperar informacion
    datos= cursor.fetchall()
    #cerrar cursor y conexion de la base de datos
    cursor.close()
    db.desconectar(conn)
    return render_template('ventas.html', datos=datos)

@app.route('/buscar_ventas', methods=['POST'])
def buscar_ventas():
    buscar_texto = request.form['buscar']
    # Conectar con la base de datos
    conn= db.conectar()
    #crear un cursor (objeto para recorrer las tablas)
    cursor= conn.cursor()
    cursor.execute('''
        SELECT * FROM consulta_ventas
        WHERE id::TEXT ILIKE %s OR "Nombre de Usuario" ILIKE %s
    ''', (f'%{buscar_texto}%', f'%{buscar_texto}%'))
    datos = cursor.fetchall()
    cursor.close()
    db.desconectar(conn)
    return render_template('ventas.html', datos=datos)

@app.route('/delete_ventas/<int:id_venta>', methods=['POST'])
def delete_ventas(id_venta):
    # Conectar con la base de datos
    conn = db.conectar()
    cursor = conn.cursor()
    try:
        # Eliminar la venta
        cursor.execute('DELETE FROM ventas WHERE id_venta=%s', (id_venta,))
        conn.commit()
        flash('Venta eliminada exitosamente', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error al eliminar la venta: {e}', 'danger')
    finally:
        cursor.close()
        db.desconectar(conn)
    return redirect(url_for('ventas'))



@app.route('/registrar_venta', methods=['GET', 'POST'])
def registrar_venta():
    form = VentaForm()
    total = 0
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Establecer la fecha y hora actuales
    form.fecha.data = datetime.now().strftime('%d-%m-%Y')  # Formato día-mes-año
    form.hora.data = datetime.now().strftime('%H:%M:%S')
    # Llenar el campo de usuario con el nombre de usuario en la sesión
    form.usuario.data = session.get('username', '')
    conn = db.conectar()
    cursor = conn.cursor()
    try:
        # Cargar opciones de productos
        cursor.execute('SELECT id_prod, nombre, precio_cu FROM producto')
        productos = cursor.fetchall()
        form.producto.choices = [(prod[0], prod[1]) for prod in productos]
        if form.validate_on_submit():
            if form.cancelar.data:
                return redirect(url_for('ventas'))
            
            # Obtener el precio del producto
            producto_id = form.producto.data
            cursor.execute('SELECT precio_cu FROM producto WHERE id_prod = %s', (producto_id,))
            precio = cursor.fetchone()[0]
            # Calcular el total
            cantidad = form.cantidad.data
            total = cantidad * precio
            # Insertar venta en la base de datos, asociando la venta al usuario autenticado
            cursor.execute('''
                INSERT INTO ventas (fecha_reali, hora_reali, fk_usuario, fk_producto, cantidad_prod, total)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (form.fecha.data, form.hora.data, session['user_id'], producto_id, cantidad, total))
            conn.commit()
            flash('Venta registrada exitosamente', 'success')
            return render_template('registrar_venta.html', form=form, total=total, success=True)
    except Exception as e:
        print(f'Error: {e}')
        flash(f'Error al registrar la venta: {e}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return render_template('registrar_venta.html', form=form, total=total, success=False)


@app.route('/imprimir_venta/<int:venta_id>', methods=['POST'])
def imprimir_venta(venta_id):
    conn = db.conectar()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT v.id_venta, v.fecha_reali, v.hora_reali, u.nombre AS usuario, 
                   u.tipo AS cargo, p.nombre AS producto, v.cantidad_prod, v.total 
            FROM ventas v
            JOIN "Usuario" u ON v.fk_usuario = u.id_usuario
            JOIN producto p ON v.fk_producto = p.id_prod
            WHERE v.id_venta = %s
        ''', (venta_id,))
        venta = cursor.fetchone()

        if venta:
            pdf_buffer = generar_pdf(venta)
            return send_file(pdf_buffer, as_attachment=True, download_name=f'venta_{venta_id}.pdf', mimetype='application/pdf')

        flash('Error: Venta no encontrada.', 'danger')
        return redirect(url_for('ventas'))
    except Exception as e:
        flash(f'Error al generar el PDF: {e}', 'danger')
        return redirect(url_for('ventas'))
    finally:
        cursor.close()
        conn.close()
