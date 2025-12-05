from database import get_database
from datetime import datetime
import hashlib

def init_db():
    db = get_database()
    if db is None:
        return

    # Clean start (optional - be careful in production!)
    print("Dropping existing collections for a clean initialization...")
    db.usuarios.drop()
    db.productos.drop()
    db.categorias.drop()
    db.pedidos.drop()
    db.carritos.drop()

    # --- Collections and Indexes ---
    
    # Usuarios (Users)
    print("Initializing 'usuarios'...")
    db.usuarios.create_index("email", unique=True)
    
    # Create an admin user and a regular customer
    users_data = [
        {
            "nombre": "Admin User",
            "email": "admin@tienda.com",
            "password": hashlib.sha256("admin123".encode()).hexdigest(), # Simple hash for demo
            "role": "admin",
            "telefono": "1234567890",
            "direcciones": [],
            "fecha_registro": datetime.utcnow(),
            "estado": "activo",
            "preferencias": {"idioma": "es", "moneda": "USD"}
        },
        {
            "nombre": "Juan Perez",
            "email": "juan@example.com",
            "password": hashlib.sha256("user123".encode()).hexdigest(),
            "role": "customer",
            "telefono": "0987654321",
            "direcciones": [
                {
                    "alias": "Casa",
                    "calle": "Calle Falsa 123",
                    "ciudad": "Springfield",
                    "pais": "Simyland",
                    "codigo_postal": "12345"
                }
            ],
            "fecha_registro": datetime.utcnow(),
            "estado": "activo",
            "preferencias": {"idioma": "es", "moneda": "USD"}
        }
    ]
    db.usuarios.insert_many(users_data)


    # Categorias (Categories)
    print("Initializing 'categorias'...")
    
    tech_category = {
        "nombre": "Tecnología",
        "slug": "tecnologia",
        "descripcion": "Gadgets y electrónicos",
        "parent_id": None,
        "fecha_creacion": datetime.utcnow()
    }
    tech_id = db.categorias.insert_one(tech_category).inserted_id

    clothing_category = {
        "nombre": "Ropa",
        "slug": "ropa",
        "descripcion": "Moda para todos",
        "parent_id": None,
        "fecha_creacion": datetime.utcnow()
    }
    clothing_id = db.categorias.insert_one(clothing_category).inserted_id
    
    # Subcategory
    laptops_category = {
        "nombre": "Laptops",
        "slug": "laptops",
        "descripcion": "Portátiles de alto rendimiento",
        "parent_id": tech_id,
        "fecha_creacion": datetime.utcnow()
    }
    laptops_id = db.categorias.insert_one(laptops_category).inserted_id


    # Productos (Products)
    print("Initializing 'productos'...")
    db.productos.create_index("sku", unique=True)
    db.productos.create_index("nombre", unique=False) # For search

    products_data = [
        {
            "sku": "LAP-001",
            "nombre": "Laptop Pro X",
            "descripcion": "La mejor laptop para desarrolladores",
            "categoria": {"id": laptops_id, "nombre": "Laptops"},
            "precio": 150000, # En centavos ($1500.00)
            "moneda": "USD",
            "stock": 50,
            "atributos": {"marca": "TechBrand", "color": "Gris Espacial", "ram": "16GB"},
            "imagenes": ["/img/products/lap001_1.jpg"],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },
        {
            "sku": "TSH-001",
            "nombre": "Camiseta Básica",
            "descripcion": "100% Algodón",
            "categoria": {"id": clothing_id, "nombre": "Ropa"},
            "precio": 2500, # En centavos ($25.00)
            "moneda": "USD",
            "stock": 200,
            "atributos": {"marca": "ClothCo", "color": "Blanco", "talla": "M"},
            "imagenes": ["/img/products/tsh001_1.jpg"],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        }
    ]
    db.productos.insert_many(products_data)

    print("Database initialization complete!")

if __name__ == "__main__":
    init_db()
