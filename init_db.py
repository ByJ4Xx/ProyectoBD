from database import get_database
from datetime import datetime
import hashlib

def init_db():
    db = get_database()
    if db is None:
        return

    # Clean start (optional - be careful in production!)
    print("Dropping existing collections for a clean initialization...")
    # Drop all existing collections to ensure a clean slate before re-initializing
    try:
        for name in db.list_collection_names():
            db.drop_collection(name)
    except Exception as e:
        print(f"Warning: could not drop all collections: {e}")

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


    # ============================
    #       CATEGORÍAS BASE
    # ============================

    # Tecnología
    tech_category = {
        "nombre": "Tecnología",
        "slug": "tecnologia",
        "descripcion": "Gadgets y electrónicos",
        "parent_id": None,
        "fecha_creacion": datetime.utcnow()
    }
    tech_id = db.categorias.insert_one(tech_category).inserted_id

    # Ropa
    clothing_category = {
        "nombre": "Ropa",
        "slug": "ropa",
        "descripcion": "Moda para todos",
        "parent_id": None,
        "fecha_creacion": datetime.utcnow()
    }
    clothing_id = db.categorias.insert_one(clothing_category).inserted_id

    # Coleccionables (antes Juguetes)
    collectibles_category = {
        "nombre": "Coleccionables",
        "slug": "coleccionables",
        "descripcion": "Figuras de acción, colecciones y artículos especiales",
        "parent_id": None,
        "fecha_creacion": datetime.utcnow()
    }
    collectibles_id = db.categorias.insert_one(collectibles_category).inserted_id


    # ============================
    #     SUBCATEGORÍAS TECNOLOGÍA
    # ============================

    # Laptops (ya existente)
    laptops_category = {
        "nombre": "Laptops",
        "slug": "laptops",
        "descripcion": "Portátiles de alto rendimiento",
        "parent_id": tech_id,
        "fecha_creacion": datetime.utcnow()
    }
    laptops_id = db.categorias.insert_one(laptops_category).inserted_id

    # Smartphones
    smartphones_category = {
        "nombre": "Smartphones",
        "slug": "smartphones",
        "descripcion": "Teléfonos inteligentes",
        "parent_id": tech_id,
        "fecha_creacion": datetime.utcnow()
    }
    smartphones_id = db.categorias.insert_one(smartphones_category).inserted_id

    # Auriculares
    headphones_category = {
        "nombre": "Auriculares",
        "slug": "auriculares",
        "descripcion": "Audífonos inalámbricos y alámbricos",
        "parent_id": tech_id,
        "fecha_creacion": datetime.utcnow()
    }
    headphones_id = db.categorias.insert_one(headphones_category).inserted_id

    # Monitores
    monitors_category = {
        "nombre": "Monitores",
        "slug": "monitores",
        "descripcion": "Pantallas para computadora",
        "parent_id": tech_id,
        "fecha_creacion": datetime.utcnow()
    }
    monitors_id = db.categorias.insert_one(monitors_category).inserted_id


    # ============================
    #     SUBCATEGORÍAS COLECCIONABLES
    # ============================

    # Figuras de Acción
    action_figures_category = {
        "nombre": "Figuras de Acción",
        "slug": "figuras-de-accion",
        "descripcion": "Figuras de colección articuladas o estáticas",
        "parent_id": collectibles_id,
        "fecha_creacion": datetime.utcnow()
    }
    action_figures_id = db.categorias.insert_one(action_figures_category).inserted_id

    # Cartas Coleccionables
    cards_category = {
        "nombre": "Cartas Coleccionables",
        "slug": "cartas",
        "descripcion": "TCG: Pokémon, Yu-Gi-Oh, MTG y más",
        "parent_id": collectibles_id,
        "fecha_creacion": datetime.utcnow()
    }
    cards_id = db.categorias.insert_one(cards_category).inserted_id


    # ============================
    #        ÍNDICES PRODUCTOS
    # ============================

    db.productos.create_index("sku", unique=True)
    db.productos.create_index("nombre", unique=False)


    # ============================
    #         PRODUCTOS
    # ============================

    products_data = [

        # ============================================
        #               L A P T O P S
        # ============================================

        {
            "sku": "LAP-001",
            "nombre": "Laptop Pro X",
            "descripcion": "La mejor laptop para desarrolladores",
            "categoria": {"id": laptops_id, "nombre": "Laptops"},
            "precio": 150000,
            "moneda": "USD",
            "stock": 50,
            "atributos": {"marca": "TechBrand", "color": "Gris Espacial", "ram": "16GB"},
            "imagenes": [
                "https://cdn-dynmedia-1.microsoft.com/is/image/microsoftcorp/B03-Surface-Laptop-13-inch-1Ed-Rational-Violet-Rear-Right"
            ],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },
        {
            "sku": "LAP-002",
            "nombre": "Laptop Ultra Slim",
            "descripcion": "Liviana y potente, ideal para estudiantes",
            "categoria": {"id": laptops_id, "nombre": "Laptops"},
            "precio": 89999,
            "moneda": "USD",
            "stock": 70,
            "atributos": {"marca": "LiteTech", "color": "Plateado", "ram": "8GB"},
            "imagenes": [
                "https://www.gatewayusa.com/cdn/shop/files/black16_f7c7d052-2222-427e-9dc6-174f2928718f.png?v=1721623728&width=1400"
            ],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },

        # ============================================
        #            S M A R T P H O N E S
        # ============================================

        {
            "sku": "SMA-001",
            "nombre": "Smartphone Max 12",
            "descripcion": "Pantalla OLED 6.7\", 5G y triple cámara",
            "categoria": {"id": smartphones_id, "nombre": "Smartphones"},
            "precio": 99900,
            "moneda": "USD",
            "stock": 120,
            "atributos": {"marca": "PhoneTech", "color": "Negro", "almacenamiento": "128GB"},
            "imagenes": [
                "https://images.fonearena.com/blog/wp-content/uploads/2022/07/Samsung-Galaxy-S22-Bora-Purple-1024x911.jpg"
            ],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },
        {
            "sku": "SMA-002",
            "nombre": "Smartphone Lite A5",
            "descripcion": "Económico, rápido y con buena cámara",
            "categoria": {"id": smartphones_id, "nombre": "Smartphones"},
            "precio": 29900,
            "moneda": "USD",
            "stock": 200,
            "atributos": {"marca": "NovaPhone", "color": "Azul", "almacenamiento": "64GB"},
            "imagenes": [
                "https://http2.mlstatic.com/D_NQ_NP_772634-MCO70066305388_062023-O.webp"
            ],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },

        # ============================================
        #            A U R I C U L A R E S
        # ============================================

        {
            "sku": "AUR-001",
            "nombre": "Auriculares ProSound",
            "descripcion": "Sonido Hi-Fi y cancelación activa de ruido",
            "categoria": {"id": headphones_id, "nombre": "Auriculares"},
            "precio": 19999,
            "moneda": "USD",
            "stock": 150,
            "atributos": {"marca": "SoundMax", "tipo": "Inalámbricos"},
            "imagenes": [
                "https://rukminim2.flixcart.com/image/480/640/xif0q/headphone/a/k/i/-original-imahyfkkhwpeb7ze.jpeg?q=90"
            ],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },
        {
            "sku": "AUR-002",
            "nombre": "Auriculares BassBoost",
            "descripcion": "Sonido profundo y batería de 30 horas",
            "categoria": {"id": headphones_id, "nombre": "Auriculares"},
            "precio": 14999,
            "moneda": "USD",
            "stock": 180,
            "atributos": {"marca": "BeatFlex", "tipo": "Over-Ear"},
            "imagenes": [
                "https://www.sony.com.co/image/5d02da5df552836db894cead8a68f5f3?fmt=pjpeg&wid=330&bgcolor=FFFFFF&bgc=FFFFFF"
            ],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },

        # ============================================
        #              M O N I T O R E S
        # ============================================

        {
            "sku": "MON-001",
            "nombre": "Monitor UltraWide 34\"",
            "descripcion": "Pantalla curva para multitarea",
            "categoria": {"id": monitors_id, "nombre": "Monitores"},
            "precio": 49999,
            "moneda": "USD",
            "stock": 40,
            "atributos": {"marca": "ViewMax", "resolución": "3440x1440"},
            "imagenes": [
                "https://www.lg.com/content/dam/channel/wcms/co/images/monitores/34wq500-b/gallery/ultrawide-34wq500-gallery-01-2010.jpg/_jcr_content/renditions/thum-1600x1062.jpeg"
            ],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },
        {
            "sku": "MON-002",
            "nombre": "Monitor Gamer 27\"",
            "descripcion": "165Hz, 1ms, ideal para gaming competitivo",
            "categoria": {"id": monitors_id, "nombre": "Monitores"},
            "precio": 29999,
            "moneda": "USD",
            "stock": 60,
            "atributos": {"marca": "GamerTech", "resolución": "1440p"},
            "imagenes": [
                "https://es-store.msi.com/cdn/shop/files/monitor-gaming-msi-mag-27c6x.png?v=1733326643&width=640"
            ],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },

        # ============================================
        #      C O L E C C I O N A B L E S
        # ============================================

        # Figuras de Acción
        {
            "sku": "FIG-001",
            "nombre": "Figura de Acción Daredevil",
            "descripcion": "Figura articulada de edición limitada",
            "categoria": {"id": action_figures_id, "nombre": "Figuras de Acción"},
            "precio": 49999,
            "moneda": "USD",
            "stock": 80,
            "atributos": {"franquicia": "Marvel", "altura": "25 cm"},
            "imagenes": ["https://alteregocomics.com/cdn/shop/files/hot-toys-marvel-daredevil-sixth-scale-figure-gallery-67eabdb51471c.jpg?v=1743442148&width=1946"],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },
        {
            "sku": "FIG-002",
            "nombre": "Punisher",
            "descripcion": "Figura articulada de edición limitada",
            "categoria": {"id": action_figures_id, "nombre": "Figuras de Acción"},
            "precio": 49999,
            "moneda": "USD",
            "stock": 50,
            "atributos": {"franquicia": "Marvel", "altura": "25 cm"},
            "imagenes": ["https://m.media-amazon.com/images/I/81W0CWI3DNL.jpg"],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },

        # Cartas coleccionables
        {
            "sku": "CAR-001",
            "nombre": "Sobre Pokémon TCG",
            "descripcion": "Sobre con 10 cartas al azar",
            "categoria": {"id": cards_id, "nombre": "Cartas Coleccionables"},
            "precio": 499,
            "moneda": "USD",
            "stock": 300,
            "atributos": {"marca": "Pokémon", "tipo": "Expansión actual"},
            "imagenes": ["https://xtremeplay.co/wp-content/uploads/2023/03/TOYCOLPOK1312_1.jpg"],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        },
        {
            "sku": "CAR-002",
            "nombre": "Exploding Kittens Party Pack",
            "descripcion": "Mazo para 10 jugadores",
            "categoria": {"id": cards_id, "nombre": "Cartas Coleccionables"},
            "precio": 1499,
            "moneda": "USD",
            "stock": 120,
            "atributos": {"marca": "Exploding Kittens", "tipo": "Party Pack"},
            "imagenes": ["https://media.falabella.com/falabellaCO/124472703_01/w=1500,h=1500,fit=pad"],
            "fecha_creacion": datetime.utcnow(),
            "visible": True,
            "reseñas": []
        }
    ]

    db.productos.insert_many(products_data)

    # ============================
    #          PEDIDOS
    # ============================
    print("Initializing 'pedidos'...")
    # NOTE: Per configuration, do not insert default/example orders.
    # The 'pedidos' collection will be created empty.

    print("Database initialization complete!")

if __name__ == "__main__":
    init_db()
