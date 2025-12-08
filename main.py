from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import get_database
from bson.objectid import ObjectId
import hashlib
from datetime import datetime
import re

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
    
    # Search and Filter Logic
    query = request.args.get('q')
    category_slug = request.args.get('category')
    
    filter_criteria = {"visible": True}
    
    if query:
        # Case-insensitive regex search
        regex = re.compile(f".*{re.escape(query)}.*", re.IGNORECASE)
        filter_criteria["$or"] = [
            {"nombre": regex},
            {"descripcion": regex}
        ]
    
    if category_slug:
        # Find category ID first
        cat = db.categorias.find_one({"slug": category_slug})
        if cat:
            # Include subcategories if any (simplified: just direct match or parent match)
            # For now, just direct match on category.id or parent_id logic if implemented fully
            # The model stores {id: ObjectId, nombre: String} in product.categoria
            # We need to match product.categoria.id == cat._id OR product.categoria.id IN subcategories
            
            # Find all subcategories IDs
            subcats = list(db.categorias.find({"parent_id": cat['_id']}))
            cat_ids = [cat['_id']] + [sc['_id'] for sc in subcats]
            
            filter_criteria["categoria.id"] = {"$in": cat_ids}

    products = list(db.productos.find(filter_criteria))
    categories = list(db.categorias.find({"parent_id": None})) # Top level categories for dropdown
    
    return render_template('index.html', products=products, categories=categories)

@app.route('/product/<product_id>')
def product_details(product_id):
    product = db.productos.find_one({"_id": ObjectId(product_id)})
    if not product:
        flash('Producto no encontrado', 'error')
        return redirect('/')
    
    # Recommendations: Same category, exclude current
    recommendations = list(db.productos.find({
        "categoria.id": product['categoria']['id'],
        "_id": {"$ne": product['_id']}
    }).limit(4))
    
    return render_template('product_details.html', product=product, recommendations=recommendations)

# --- Cart Routes ---

@app.route('/cart')
def view_cart():
    if 'user' not in session:
        flash('Debes iniciar sesión para ver tu carrito', 'error')
        return redirect('/login')
    
    user_id = ObjectId(session['user']['id'])
    
    # Fetch cart from DB
    # Note: Model says "carrito_actual" in User, or "Carritos" collection.
    # Let's use Carritos collection: {cliente_id: ..., items: [...]}
    cart = db.carritos.find_one({"cliente_id": user_id})
    
    cart_items = []
    total = 0
    
    if cart:
        cart_items = cart['items']
        # Calculate total dynamically or trust DB? Let's recalc for display
        for item in cart_items:
            total += item['precio_unitario'] * item['cantidad']
            # Convert ObjectId to string for template-friendly URLs
            try:
                item['producto_id_str'] = str(item.get('producto_id'))
            except Exception:
                item['producto_id_str'] = item.get('producto_id')
            
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/cart/add/<product_id>')
def add_to_cart(product_id):
    if 'user' not in session:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {"error": "auth_required"}, 401
        flash('Debes iniciar sesión para agregar productos al carrito', 'error')
        return redirect('/login')
    
    user_id = ObjectId(session['user']['id'])
    product = db.productos.find_one({"_id": ObjectId(product_id)})
    
    if not product:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {"error": "product_not_found"}, 404
        return redirect('/')

    cart = db.carritos.find_one({"cliente_id": user_id})
    
    item_data = {
        "producto_id": product['_id'],
        "nombre": product['nombre'],
        "sku": product.get('sku', ''),
        "cantidad": 1,
        "precio_unitario": product['precio'],
        "atributos": {} 
    }

    if cart:
        existing_item = next((item for item in cart['items'] if item['producto_id'] == product['_id']), None)
        
        if existing_item:
            db.carritos.update_one(
                {"_id": cart['_id'], "items.producto_id": product['_id']},
                {"$inc": {"items.$.cantidad": 1}}
            )
        else:
            db.carritos.update_one(
                {"_id": cart['_id']},
                {"$push": {"items": item_data}}
            )
    else:
        new_cart = {
            "cliente_id": user_id,
            "items": [item_data],
            "subtotal": 0, 
            "descuentos": [],
            "fecha_actualizacion": datetime.utcnow()
        }
        db.carritos.insert_one(new_cart)
        
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return {"success": True, "message": "Producto agregado"}
        
    flash('Producto agregado al carrito', 'success')
    return redirect('/cart')

@app.route('/cart/remove/<product_id>')
def remove_from_cart(product_id):
    if 'user' not in session:
        return redirect('/login')
        
    user_id = ObjectId(session['user']['id'])
    db.carritos.update_one(
        {"cliente_id": user_id},
        {"$pull": {"items": {"producto_id": ObjectId(product_id)}}}
    )
    return redirect('/cart')

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user' not in session:
        return redirect('/login')
    
    user_id = ObjectId(session['user']['id'])
    cart = db.carritos.find_one({"cliente_id": user_id})
    
    if not cart or not cart['items']:
        flash('El carrito está vacío', 'error')
        return redirect('/cart')
        
    # Calculate totals
    total = 0
    items_snapshot = []
    
    for item in cart['items']:
        total += item['precio_unitario'] * item['cantidad']
        items_snapshot.append(item)
        
        # Decrease stock
        db.productos.update_one(
            {"_id": item['producto_id']},
            {"$inc": {"stock": -item['cantidad']}}
        )
    
    user = db.usuarios.find_one({"_id": user_id})
    if not user:
        # If session references a user that no longer exists in DB, stop checkout
        flash('No se encontró el usuario. Por favor inicia sesión de nuevo.', 'error')
        return redirect('/login')
    
    # Create Order
    new_order = {
        "usuario_id": user_id,
        "numero_pedido": f"ORD-{int(datetime.utcnow().timestamp())}",
        "items": items_snapshot,
        "subtotal": total,
        "impuestos": 0,
        "descuentos": 0,
        "total": total,
        "estado": "CREADO",
        "direccion_envio": user.get('direcciones', [{}])[0] if user.get('direcciones') else {},
        "pago": {"metodo": "simulado", "estado": "pendiente", "fecha": datetime.utcnow()},
        "fecha_pedido": datetime.utcnow()
    }
    
    order_id = db.pedidos.insert_one(new_order).inserted_id
    
    # Clear Cart
    db.carritos.delete_one({"_id": cart['_id']})
    
    flash('¡Pedido realizado con éxito!', 'success')
    return redirect(url_for('order_details', order_id=str(order_id)))

@app.route('/order/<order_id>')
def order_details(order_id):
    if 'user' not in session:
        return redirect('/login')
        
    order = db.pedidos.find_one({"_id": ObjectId(order_id)})
    
    if not order:
        flash('Pedido no encontrado', 'error')
        return redirect('/dashboard')
        
    # Ensure user owns order or is admin
    if str(order['usuario_id']) != session['user']['id'] and session['user']['role'] != 'admin':
        flash('No tienes permiso para ver este pedido', 'error')
        return redirect('/dashboard')
        
    # Prepare items separately to avoid Jinja resolving dict.method 'items'
    order_items = order.get('items', []) if isinstance(order, dict) else []

    # Prepare a safe formatted date string
    fecha = order.get('fecha_pedido') if isinstance(order, dict) else None
    fecha_str = fecha.strftime('%Y-%m-%d %H:%M') if fecha else ''

    return render_template('order_details.html', order=order, items=order_items, fecha_str=fecha_str)


# --- Auth & Admin ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_pw = hash_password(password)
        
        user = get_user_by_email(email)
        
        if user and user['password'] == hashed_pw:
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
    pedidos = list(db.pedidos.find({"usuario_id": user_id}))

    # Add string IDs and formatted date to each pedido for template safety
    for p in pedidos:
        try:
            p['pedido_id_str'] = str(p.get('_id'))
        except Exception:
            p['pedido_id_str'] = p.get('_id')
        fecha = p.get('fecha_pedido')
        try:
            p['fecha_str'] = fecha.strftime('%Y-%m-%d') if fecha else ''
        except Exception:
            p['fecha_str'] = ''
        # Ensure total exists
        p['total_display'] = p.get('total', 0)

    return render_template('dashboard.html', pedidos=pedidos)

@app.route('/admin')
def admin():
    if 'user' not in session or session['user']['role'] != 'admin':
        flash('Acceso denegado. Se requieren permisos de administrador.', 'error')
        return redirect('/')
    
    # Analytics
    pipeline_sales = [
        {"$group": {"_id": None, "total": {"$sum": "$total"}}}
    ]
    sales_result = list(db.pedidos.aggregate(pipeline_sales))
    total_sales = sales_result[0]['total'] if sales_result else 0
    
    total_orders = db.pedidos.count_documents({})
    low_stock_count = db.productos.count_documents({"stock": {"$lt": 10}})
    
    recent_orders = list(db.pedidos.find().sort("fecha_pedido", -1).limit(10))
    categorias = list(db.categorias.find())
    
    return render_template('admin.html', 
                           categorias=categorias,
                           total_sales=total_sales,
                           total_orders=total_orders,
                           low_stock_count=low_stock_count,
                           recent_orders=recent_orders)


@app.route('/admin/analytics')
def admin_analytics():
    if 'user' not in session or session['user']['role'] != 'admin':
        flash('Acceso denegado. Se requieren permisos de administrador.', 'error')
        return redirect('/')

    # Total sales (revenue) - reuse approach from /admin
    pipeline_sales = [{"$group": {"_id": None, "total": {"$sum": "$total"}}}]
    sales_result = list(db.pedidos.aggregate(pipeline_sales))
    total_sales = sales_result[0]['total'] if sales_result else 0

    # Number of registered customers (role == 'customer')
    num_customers = db.usuarios.count_documents({"role": "customer"})

    # Top products by quantity and revenue
    prod_pipeline = [
        {"$unwind": "$items"},
        {"$group": {
            "_id": "$items.producto_id",
            "quantity": {"$sum": "$items.cantidad"},
            "revenue": {"$sum": {"$multiply": ["$items.cantidad", "$items.precio_unitario"]}}
        }},
        {"$sort": {"quantity": -1}},
        {"$limit": 5}
    ]
    top_aggr = list(db.pedidos.aggregate(prod_pipeline))

    top_products = []
    for row in top_aggr:
        try:
            prod = db.productos.find_one({"_id": row['_id']})
            top_products.append({
                "_id": str(row['_id']),
                "nombre": prod['nombre'] if prod else 'Desconocido',
                "quantity": int(row.get('quantity', 0)),
                "revenue": int(row.get('revenue', 0))
            })
        except Exception:
            top_products.append({
                "_id": str(row['_id']),
                "nombre": 'Desconocido',
                "quantity": int(row.get('quantity', 0)),
                "revenue": int(row.get('revenue', 0))
            })

    best_product = top_products[0] if top_products else None

    # Category with most sales (by revenue)
    cat_pipeline = [
        {"$unwind": "$items"},
        {"$lookup": {
            "from": "productos",
            "localField": "items.producto_id",
            "foreignField": "_id",
            "as": "prod"
        }},
        {"$unwind": "$prod"},
        {"$group": {
            "_id": "$prod.categoria.id",
            "quantity": {"$sum": "$items.cantidad"},
            "revenue": {"$sum": {"$multiply": ["$items.cantidad", "$items.precio_unitario"]}}
        }},
        {"$sort": {"revenue": -1}},
        {"$limit": 1}
    ]
    cat_aggr = list(db.pedidos.aggregate(cat_pipeline))
    top_category = None
    if cat_aggr:
        cat_row = cat_aggr[0]
        cat_doc = None
        try:
            cat_doc = db.categorias.find_one({"_id": cat_row['_id']})
        except Exception:
            cat_doc = None
        top_category = {
            "_id": str(cat_row['_id']) if cat_row.get('_id') else None,
            "nombre": cat_doc['nombre'] if cat_doc else 'Desconocida',
            "quantity": int(cat_row.get('quantity', 0)),
            "revenue": int(cat_row.get('revenue', 0))
        }

    # Sales by month (YYYY-MM) — sum totals per month
    month_pipeline = [
        {"$match": {"fecha_pedido": {"$exists": True}}},
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m", "date": "$fecha_pedido"}},
            "total": {"$sum": "$total"}
        }},
        {"$sort": {"_id": 1}}
    ]
    month_aggr = list(db.pedidos.aggregate(month_pipeline))
    sales_by_month = [{"month": m['_id'], "total": int(m['total'])} for m in month_aggr]

    return render_template('analytics.html',
                           total_sales=total_sales,
                           num_customers=num_customers,
                           top_products=top_products,
                           best_product=best_product,
                           top_category=top_category,
                           sales_by_month=sales_by_month)

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
