from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import get_database
from bson.objectid import ObjectId
import hashlib
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super_secret_key_change_me' # Required for session

# Database Connection
db = get_database()

# --- Helpers ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_by_email(email):
    if db is None: return None
    return db.usuarios.find_one({"email": email})

# --- Routes ---

@app.route('/')
def index():
    if db is None:
        return "Database Connection Error", 500
    products = list(db.productos.find({"visible": True}))
    return render_template('index.html', products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_pw = hash_password(password)
        
        user = get_user_by_email(email)
        
        if user and user['password'] == hashed_pw:
            # Store minimal user info in session using string representations of ObjectIds
            session['user'] = {
                'id': str(user['_id']),
                'nombre': user['nombre'],
                'email': user['email'],
                'role': user.get('role', 'customer')
            }
            flash('Bienvenido!', 'success')
            return redirect('/')
        else:
            flash('Credenciales incorrectas', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        telefono = request.form['telefono']
        
        if get_user_by_email(email):
            flash('El email ya está registrado', 'error')
            return redirect(url_for('register'))
            
        new_user = {
            "nombre": nombre,
            "email": email,
            "password": hash_password(password),
            "role": "customer",
            "telefono": telefono,
            "direcciones": [],
            "fecha_registro": datetime.utcnow(),
            "estado": "activo"
        }
        
        db.usuarios.insert_one(new_user)
        flash('Cuenta creada exitosamente. Por favor inicia sesión.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    
    user_id = ObjectId(session['user']['id'])
    # Fetch orders (pedidos)
    pedidos = list(db.pedidos.find({"usuario_id": user_id}))
    return render_template('dashboard.html', pedidos=pedidos)

@app.route('/admin')
def admin():
    if 'user' not in session or session['user']['role'] != 'admin':
        flash('Acceso denegado. Se requieren permisos de administrador.', 'error')
        return redirect('/')
    
    categorias = list(db.categorias.find())
    return render_template('admin.html', categorias=categorias)

@app.route('/admin/add_product', methods=['POST'])
def add_product():
    if 'user' not in session or session['user']['role'] != 'admin':
        return redirect('/')
    
    nombre = request.form['nombre']
    sku = request.form['sku']
    descripcion = request.form['descripcion']
    precio = int(request.form['precio'])
    stock = int(request.form['stock'])
    categoria_id = request.form['categoria_id']
    imagen_url = request.form.get('imagen_url')
    
    # Get category name for embedding
    cat = db.categorias.find_one({"_id": ObjectId(categoria_id)})
    
    new_product = {
        "sku": sku,
        "nombre": nombre,
        "descripcion": descripcion,
        "categoria": {"id": ObjectId(categoria_id), "nombre": cat['nombre'] if cat else "General"},
        "precio": precio,
        "moneda": "USD",
        "stock": stock,
        "imagenes": [imagen_url] if imagen_url else [],
        "fecha_creacion": datetime.utcnow(),
        "visible": True,
        "reseñas": []
    }
    
    try:
        db.productos.insert_one(new_product)
        flash('Producto agregado correctamente', 'success')
    except Exception as e:
        flash(f'Error al agregar producto: {str(e)}', 'error')
        
    return redirect('/admin')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
